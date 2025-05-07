"""Código para estimar o X e Y do ROV
Converte acelerações em deslocamento
Mantem o ROV no centro do referêncial
Permite juntar as image
"""

import numpy as np
import time

# Inicializar posição e orientação
rov_x, rov_y = 0, 0  # O ROV começa no centro do referencial
yaw_angle = 0  # Direção inicial (Yaw)

# Função para simular leitura da IMU
def read_imu():
    """
    Simula leituras da IMU: aceleração em X e Y e ângulo de Yaw.
    Em um ROV real, isto viria da biblioteca pymavlink ou sensor IMU real.
    """
    simulated_accel_x = np.random.uniform(-0.02, 0.02)  # Pequena aceleração aleatória
    simulated_accel_y = np.random.uniform(-0.02, 0.02)
    simulated_yaw = np.random.uniform(-5, 5)  # Pequena variação no ângulo

    return {"accel_x": simulated_accel_x, "accel_y": simulated_accel_y, "yaw": simulated_yaw}

# Estimativa de posição relativa
def estimate_position(dt=0.1):
    global rov_x, rov_y, yaw_angle

    imu_data = read_imu()
    accel_x = imu_data["accel_x"]
    accel_y = imu_data["accel_y"]
    yaw_angle += imu_data["yaw"]  # Atualiza o ângulo de rotação

    # Calcular deslocamento com base no ângulo Yaw
    dx = accel_x * np.cos(np.radians(yaw_angle)) - accel_y * np.sin(np.radians(yaw_angle))
    dy = accel_x * np.sin(np.radians(yaw_angle)) + accel_y * np.cos(np.radians(yaw_angle))

    # Atualizar posição relativa ao ROV
    rov_x += dx * dt
    rov_y += dy * dt

    return {"x": rov_x, "y": rov_y, "yaw": yaw_angle}

# Simular leitura de posição ao longo do tempo
for _ in range(50):  # Simular 50 leituras
    pos = estimate_position()
    print(f"Posição relativa: X={pos['x']:.2f} m, Y={pos['y']:.2f} m, Yaw={pos['yaw']:.2f}°")
    time.sleep(0.1)
