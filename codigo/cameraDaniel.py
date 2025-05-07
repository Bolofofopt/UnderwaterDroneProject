import cv2
import numpy as np
import time
from threading import Thread
import queue

# Configuração
largura_janela, altura_janela = 960, 540
largura_proc, altura_proc = 1280, 720
max_tamanho_fila = 5
fps_desejado = 30

# Intervalos para detetar vermelho
limite_inferior1 = np.array([0, 150, 100])
limite_superior1 = np.array([10, 255, 255])
limite_inferior2 = np.array([160, 130, 0])
limite_superior2 = np.array([179, 255, 255])

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)) #remover ruidos

fonte = cv2.FONT_HERSHEY_SIMPLEX
tamanho_fonte = 0.6
cor_fonte = (0, 255, 0)
espessura_fonte = 2

# GStreamer pipeline (adaptado ao Companion da Blue Robotics)
GSTREAMER_PIPELINE = (
    "udpsrc port=5600 ! application/x-rtp, encoding-name=H264, payload=96 ! "
    "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
)

class LeitorVideo:
    def __init__(self, origem):
        """_summary_

        Args:
            origem (_type_): _description_

        Raises:
            Exception: _description_
        """
        self.cap = cv2.VideoCapture(origem, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise Exception("Não foi possível abrir o stream de vídeo do BlueROV2.")
        self.fila = queue.Queue(maxsize=max_tamanho_fila)
        self.parado = False

        self.fps_video = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps_limite = min(fps_desejado, self.fps_video) if self.fps_video > 0 else fps_desejado
        self.atraso_fotograma = 1.0 / self.fps_limite

    def iniciar(self):
        """_summary_
            inicar a thread que lê os frames
        """
        Thread(target=self.actualizar, daemon=True).start()
        return self

    def actualizar(self):
        """_summary_
            Lê os frames do stream de vídeo e coloca na fila
            Se a fila estiver cheia, espera até que haja espaço
            Se o stream de vídeo acabar, para a thread
        """
        tempo_ultimo_frame = time.time()
        while not self.parado:
            if not self.fila.full():
                tempo_atual = time.time()
                if tempo_atual - tempo_ultimo_frame < self.atraso_fotograma:
                    time.sleep(0.001)
                    continue
                ret, frame = self.cap.read()
                if not ret:
                    self.parado = True
                    break
                self.fila.put((frame, tempo_atual))
                tempo_ultimo_frame = tempo_atual
            else:
                time.sleep(0.001)

    def ler(self):
        """_summary_
            Lê o frame mais recente da fila
            Se a fila estiver vazia, retorna None
        """
        return self.fila.get() if not self.fila.empty() else (None, None)

    def parar(self):
        self.parado = True
        self.cap.release()

def principal():
    """_summary_
        Função principal que inicia o leitor de vídeo e processa os frames
    """

    stream = LeitorVideo(GSTREAMER_PIPELINE).iniciar()

    nome_janela = "Detecção Vermelha - BlueROV2"
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, largura_janela, altura_janela)

    lista_fps = []

    try:
        while not stream.parado:
            frame, tempo_frame = stream.ler()
            if frame is None:
                time.sleep(0.01)
                continue

            frame_reduzido = cv2.resize(frame, (largura_proc, altura_proc))
            hsv = cv2.cvtColor(frame_reduzido, cv2.COLOR_BGR2HSV)

            mascara1 = cv2.inRange(hsv, limite_inferior1, limite_superior1)
            mascara2 = cv2.inRange(hsv, limite_inferior2, limite_superior2)
            mascara = cv2.bitwise_or(mascara1, mascara2)

            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

            M = cv2.moments(mascara)

            escala_x = frame.shape[1] / largura_proc
            escala_y = frame.shape[0] / altura_proc
            frame_exibicao = cv2.resize(frame, (largura_janela, altura_janela))

            if M["m00"] > 0:
                cX_reduzido = int(M["m10"] / M["m00"])
                cY_reduzido = int(M["m01"] / M["m00"])
                cX = int(cX_reduzido * escala_x)
                cY = int(cY_reduzido * escala_y)
                cX_exib = int(cX * largura_janela / frame.shape[1])
                cY_exib = int(cY * altura_janela / frame.shape[0])
                cv2.circle(frame_exibicao, (cX_exib, cY_exib), 2, cor_fonte, 2)
                cv2.putText(frame_exibicao, f"Centroide: ({cX}, {cY})",
                            (cX_exib + 20, cY_exib), fonte, tamanho_fonte, cor_fonte, espessura_fonte)

            tempo_agora = time.time()
            if tempo_frame > 0:
                fps_atual = 1 / (tempo_agora - tempo_frame)
                lista_fps.append(fps_atual)
                if len(lista_fps) > 10:
                    lista_fps.pop(0)
                media_fps = sum(lista_fps) / len(lista_fps)
                cv2.putText(frame_exibicao, f"FPS: {media_fps:.1f} / Limite: {stream.fps_limite:.1f}",
                            (10, 30), fonte, tamanho_fonte, cor_fonte, espessura_fonte)

            cv2.imshow(nome_janela, frame_exibicao)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        stream.parar()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    principal()