import numpy as np
import matplotlib.pyplot as plt
import time
import csv
from scipy.interpolate import griddata

# Inicializar posição e orientação
rov_x, rov_y = 0, 0  # O ROV começa no centro do referencial
yaw_angle = 0  # Direção inicial (Yaw)

# Criar arquivo CSV para armazenar os dados
csv_filename = "rov_navigation_data.csv"
with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["X (m)", "Y (m)", "Yaw (graus)", "Profundidade (m)"])

# Simula leituras da IMU (substituir por leitura real)
def read_imu():
    simulated_accel_x = np.random.uniform(-0.02, 0.02)
    simulated_accel_y = np.random.uniform(-0.02, 0.02)
    simulated_yaw = np.random.uniform(-5, 5)
    return {"accel_x": simulated_accel_x, "accel_y": simulated_accel_y, "yaw": simulated_yaw}

# Simula leitura do altímetro ou eco-sonda
def read_depth_sensor():
    return np.random.uniform(10, 50)  # Profundidade entre 10m e 50m

# Estimativa de posição relativa e gravação dos dados
def estimate_position(dt=0.1):
    global rov_x, rov_y, yaw_angle

    imu_data = read_imu()
    accel_x = imu_data["accel_x"]
    accel_y = imu_data["accel_y"]
    yaw_angle += imu_data["yaw"]

    dx = accel_x * np.cos(np.radians(yaw_angle)) - accel_y * np.sin(np.radians(yaw_angle))
    dy = accel_x * np.sin(np.radians(yaw_angle)) + accel_y * np.cos(np.radians(yaw_angle))

    rov_x += dx * dt
    rov_y += dy * dt
    depth = read_depth_sensor()

    with open(csv_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([rov_x, rov_y, yaw_angle, depth])

    return {"x": rov_x, "y": rov_y, "yaw": yaw_angle, "depth": depth}

# Geração do mapa batimétrico
def generate_tbn_map(samples=100):
    x_data, y_data, depth_data = [], [], []

    print("Coletando dados do sensor...")
    for _ in range(samples):
        pos = estimate_position()
        x_data.append(pos["x"])
        y_data.append(pos["y"])
        depth_data.append(pos["depth"])
        time.sleep(0.05)

    print("Coleta de dados concluída!")

    grid_x, grid_y = np.meshgrid(
        np.linspace(min(x_data), max(x_data), 100),
        np.linspace(min(y_data), max(y_data), 100)
    )
    grid_depth = griddata((x_data, y_data), depth_data, (grid_x, grid_y), method="cubic")

    plt.figure(figsize=(8, 6))
    contour = plt.contourf(grid_x, grid_y, grid_depth, cmap="viridis", levels=20)
    plt.colorbar(contour, label="Profundidade (m)")
    plt.scatter(x_data, y_data, c="red", marker="x", label="Leituras do Sensor")
    plt.scatter(0, 0, c="black", marker="o", s=100, label="Posição Inicial do ROV")  # Marca o ponto central
    plt.xlabel("Posição X (m)")
    plt.ylabel("Posição Y (m)")
    plt.title("Mapa de Navegação Baseado no Terreno (TBN)")
    plt.legend()
    plt.show()

# Executar a geração do mapa batimétrico
while True:
    generate_tbn_map()
    time.sleep(2)
