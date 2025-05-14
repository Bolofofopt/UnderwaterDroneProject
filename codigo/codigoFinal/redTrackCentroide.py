import cv2 # type: ignore
import numpy as np

class redTrackCentroideError:
    def __init__(self):
        self.lower_red1 = np.array([0, 100, 50])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 100, 50])
        self.upper_red2 = np.array([179, 255, 255])
        self.kernel = np.ones((5, 5), np.uint8)

    def process_image(self, image_bgr):
        """
            Deteta objetos vermelhos e retorna área, centroide e máscara.
        Args:
            Im_bgr (_type_): IMAGEM
        Returns:
            _type_: AREA, CENTROIDE, MASCARA
        """
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, self.kernel)

        # Não é necessário, mas pode ajudar a melhorar a deteção
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return 0, None, mask_clean, image_bgr

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        M = cv2.moments(largest)
        if M["m00"] == 0:
            centroid = None
        else:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroid = (cy, cx)

            # Visualização
            cv2.drawContours(image_bgr, [largest], -1, (0, 255, 0), 2)
            cv2.circle(image_bgr, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(image_bgr, f"Area: {area:.0f}", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return area, centroid, mask_clean, image_bgr

    def calcular_erro(self, centroide_alvo, imagem_shape):
        """
            Retorna o erro (dy, dx) entre o centroide do alvo e o centro da imagem.
            dy > 0 => alvo está abaixo do centro.
            dx > 0 => alvo está à direita do centro.
        """
        h, w = imagem_shape[:2]
        centro_imagem = (h / 2, w / 2)

        if centroide_alvo is None:
            return None

        # correção professor
        dy = centro_imagem[0] - centroide_alvo[0]
        dx = centro_imagem[1] - centroide_alvo[1]
        """GPT
        dy = centroide_alvo[0] - centro_imagem[0]
        dx = centroide_alvo[1] - centro_imagem[1]
        """
        return dy, dx

if __name__ == "__main__":
    tracker = redTrackCentroideError()