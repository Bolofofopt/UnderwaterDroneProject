import time
from ROVlateralvertical import ROVactuators, ROVsensors
from pidController import PIDController # type: ignore
from redTrackCentroide import redTrackCentroideError # type: ignore


sensors = ROVsensors()
actuadores = ROVactuators()

pidLateral = PIDController(kp=1.0, ki=0.0, kd=0.0)
pidVertical = PIDController(kp=0.5, ki=0.0, kd=0)
tracker = redTrackCentroideError()

pingSensor = sensors.connectPing1D("192.168.2.2", 9090)
mavLink = sensors.connectMAVLINK("0.0.0.0", 14550)
sensors.connectCamera()

threshold_centralidade = 30  # px tolerância para considerar centrado
frames_extra_avanço = 20     # número de ciclos para avançar após perder o arco
contador_avanço = 0


try: 
    while True:
        frame = sensors.get_camera_frame()
        area, centroide, mask = tracker.process_image(frame)
        
        if area > 0:
            erro = tracker.calcular_erro(centroide, frame.shape)
            
            if erro:
                dy, dx = erro
                saida_pid_vertical = pidVertical.update(dy)
                saida_pid_lateral = pidLateral.update(dx)
                print(f"Erro: {erro} | PID Vertical: {saida_pid_vertical:.2f} | PID Lateral: {saida_pid_lateral:.2f}")
                
                if abs(dx) < threshold_centralidade and abs(dy) < threshold_centralidade:
                    print("Centroide centrado")
                    actuadores.set_thrust(
                        thrust_z=saida_pid_vertical,
                        thrust_y=saida_pid_lateral,
                        thrust_x=0.2,  # pequeno impulso para frente
                        connectionMAVLINK=mavLink
                    )
                else: 
                    print("Centroide fora do centro")
                    actuadores.set_thrust(thrust_z=saida_pid_vertical, thrust_y=saida_pid_lateral, connectionMAVLINK=mavLink)
                
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
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Controle de profundidade interrompido pelo usuário.")
    sensors.release_camera()
