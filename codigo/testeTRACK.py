from ROVlateralvertical import ROVactuators, ROVsensors



sensors = ROVsensors()
actuadores = ROVactuators()
pidLateral = PIDController(kp=1.0, ki=0.0, kd=0.0)
pidVertical = PIDController(kp=0.5, ki=0.0, kd=0.1)




tracker = RedObjectTracker()
actuadores = ROVactuators()

# Supondo que tens frame e conexão MAVLink
area, centroide, mask = tracker.process_image(frame)
erro = tracker.calcular_erro(centroide, frame.shape)

if erro:
    dy, dx = erro
    saida_pid_vertical = pid_vertical.update(dy)
    saida_pid_lateral = pid_lateral.update(dx)

    actuadores.set_thrust(saida_pid_vertical, saida_pid_lateral, connectionMAVLINK)
