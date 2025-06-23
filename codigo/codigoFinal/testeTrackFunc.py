import time
import cv2
import csv
import numpy as np
import os
import vlc  # type: ignore
from ROVlateralvertical import ROVactuators, ROVsensors
from pidController import PIDController
from redTrackCentroide import redTrackCentroideError


def inicializar_componentes():
    sensors = ROVsensors()
    actuadores = ROVactuators()
    pidLateral = PIDController(kp=0.3, ki=0.0, kd=0.0)
    pidVertical = PIDController(kp=0.2, ki=0.0, kd=0.0)
    tracker = redTrackCentroideError()
    #pingSensor = sensors.connectPing1D("192.168.2.2", 9090)
    mavLink = sensors.connectMAVLINK("0.0.0.0", 14550)

    os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
    options = ["--network-caching=100", "--drop-late-frames", "--skip-frames"]
    instance = vlc.Instance(*options)
    # media = instance.media_new(SDPfile)
    media = instance.media_new(
        r"C:\Users\henri\Documents\Articles-Documents\Documents\Projects\Faculdade\ProjetoSubmarino\codigo\codigoFinal\camararov.sdp"
    )
    player = instance.media_player_new()
    player.set_media(media)
    player.play()
    time.sleep(2)

    return sensors, actuadores, pidLateral, pidVertical, tracker, mavLink, player

def inicializar_csv(nome_ficheiro='pid_output_log.csv'):
    csv_file = open(nome_ficheiro, mode='w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'Frame', 'Elapsed_Time(s)',
        'Centroide_X', 'Centroide_Y',
        'Erro_X', 'Erro_Y',
        'PID_Lateral_Output', 'PID_Vertical_Output'
    ])
    return csv_file, csv_writer

def processar_frame(frame, tracker):
    area, centroide, mask, annotated_frame = tracker.process_image(frame)
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    composite = np.hstack((annotated_frame, mask_bgr))
    return area, centroide, composite

def main():
    (
        sensors, actuadores, pidLateral, pidVertical,
        tracker, mavLink, player
    ) = inicializar_componentes()
    sensors.armROV(connectionMAVLINK=mavLink)

    out = tracker.inicializar_gravacao_video()
    csv_file, csv_writer = inicializar_csv()

    threshold_centralidade = 60
    frames_extra_avanço = 20
    contador_avanço = 0

    frame_counter = 0
    start_time = time.time()

    try:
        while True:
            #frame = sensors.get_camera_frame()
            frame = tracker.conversion(player)
            if frame is None:
                print("Sem frame capturado.")
                continue

            area, centroide, composite = processar_frame(frame, tracker)
            out.write(composite)

            elapsed_time = time.time() - start_time
            erro_x, erro_y = 0, 0
            pid_lateral_output, pid_vertical_output = 0.0, 0.0

            if area > 0 and centroide is not None:
                dy, dx = tracker.calcular_erro(centroide, frame.shape)
                erro_x, erro_y = dx, dy

                pid_vertical_output = pidVertical.update(dy)
                pid_lateral_output = pidLateral.update(dx)

                print(f"Erro: {(dy, dx)} | PID Vertical: {pid_vertical_output:.2f} | PID Lateral: {pid_lateral_output:.2f}")

                if abs(dx) < threshold_centralidade and abs(dy) < threshold_centralidade:
                    print("Centroide centrado")
                    actuadores.set_thrust(
                        thrust_z=pid_vertical_output,
                        thrust_y=pid_lateral_output,
                        thrust_x=0.2,
                        connectionMAVLINK=mavLink
                    )
                else:
                    print("Centroide fora do centro")
                    print(pid_lateral_output, pid_vertical_output)
                    actuadores.set_thrust(
                        thrust_z=pid_vertical_output,
                        thrust_y=pid_lateral_output,
                        thrust_x=0.2,
                        connectionMAVLINK=mavLink
                    )

                contador_avanço = frames_extra_avanço

            else:
                if contador_avanço > 0:
                    print("Passou o Arco?! Avançar...")
                    actuadores.set_thrust(
                        thrust_z=0.0,
                        thrust_y=0.0,
                        thrust_x=0.2,
                        connectionMAVLINK=mavLink
                    )
                    contador_avanço -= 1
                else:
                    print("Sem arco")
                    actuadores.set_thrust(
                        thrust_z=0.0,
                        thrust_y=0.0,
                        thrust_x=0.0,
                        connectionMAVLINK=mavLink
                    )

            if centroide:
                csv_writer.writerow([
                    frame_counter, f"{elapsed_time:.2f}",
                    centroide[0], centroide[1],
                    erro_x, erro_y,
                    f"{pid_lateral_output:.2f}",
                    f"{pid_vertical_output:.2f}"
                ])

            frame_counter += 1

    except KeyboardInterrupt:
        print("Interrompido pelo usuário.")

    finally:
        #sensors.release_camera()
        sensors.disarmROV(connectionMAVLINK=mavLink)
        out.release()
        csv_file.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()