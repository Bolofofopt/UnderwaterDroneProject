import time
from pymavlink import mavutil

# Conectar ao ROV via MAVLink
connectionMAVLINK = mavutil.mavlink_connection('udp:192.168.2.1:14550')

# Esperar heartbeat
print("A aguardar heartbeat...")
connectionMAVLINK.wait_heartbeat()
print("Ligado ao sistema", connectionMAVLINK.target_system)
connectionMAVLINK.set_mode('MANUAL')

# Armar o ROV
connectionMAVLINK.mav.command_long_send(
    connectionMAVLINK.target_system,
    connectionMAVLINK.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)
print("A armar...")
time.sleep(2)

# Definir valores de controlo manual
# X = forward/backward (positivo = frente)
# Y = lateral (positivo = direita)
# Z = vertical (positivo = subir) — mas no ArduSub Z é invertido
# Yaw = 0 (sem rotação)
# Buttons = 0 (sem botões pressionados)

x_mav = 1000     # velocidade para frente (varia de -1000 a 1000)
y_mav = 0       # sem movimento lateral
z_mav = 1000     # 500 = manter profundidade (neutro no ArduSub)
yaw = 0
buttons = 0

# Enviar comando para mover para frente
print("A mover para a frente por 3 segundos...")
start = time.time()
while time.time() - start < 3:
    connectionMAVLINK.mav.manual_control_send(
        connectionMAVLINK.target_system,
        x_mav, y_mav, z_mav,
        yaw, buttons
    )
    time.sleep(0.1)  # enviar a cada 100ms

# Parar movimento (x=0)
print("A parar o ROV...")
connectionMAVLINK.mav.manual_control_send(
    connectionMAVLINK.target_system,
    0, 0, z_mav,
    yaw, buttons
)

# Desarmar o ROV
connectionMAVLINK.mav.command_long_send(
    connectionMAVLINK.target_system,
    connectionMAVLINK.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 0, 0, 0, 0, 0, 0, 0
)
print("ROV desarmado.")
