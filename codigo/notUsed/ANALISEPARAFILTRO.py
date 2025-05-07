"""Passo 1: Capturar a profundidade do ROV usando o VFR_HUD (Vertical Frame HUD).

Passo 2: Capturar os dados do IMU (ATTITUDE) quando a profundidade estiver constante.

Passo 3: Armazenar os dados em um CSV.

Passo 4: Gerar gráficos para analisar se há ruído excessivo."""
import time
import pandas as pd # type: ignore
import matplotlib.pyplot as plt
from ROV import ROVsensors
sensors = ROVsensors()


depth_threshold = 0.05  # Margem de variação de profundidade aceitável
data = []

IPmav = "0.0.0.0"
PORTmav = 14550

def collect_data(duration=30):
    print(f"Coletando dados por {duration} segundos...")
    start_time = time.time()
    stable_depth = None

    MAVLINKconnection = sensors.connectMAVLINK(IP=IPmav, PORT=PORTmav)

    while time.time() - start_time < duration:
        # Captura a profundidade
        depth_msg = MAVLINKconnection.recv_match(type='VFR_HUD', blocking=True)

        if depth_msg:
            current_depth = depth_msg.alt  # Profundidade atual
            if stable_depth is None:
                stable_depth = current_depth  # Define uma profundidade inicial

            # Verifica se a profundidade é estável
            if abs(current_depth - stable_depth) <= depth_threshold:
                attitudeData = sensors.get_pitch_roll(connectionMAVLINK=MAVLINKconnection)
                print(f"Processed IMU Data CODIGOCOLLECT: {attitudeData}")
    
    # Salvar os dados em um CSV
    df = pd.DataFrame(data, columns=['timestamp', 'depth', 'roll', 'pitch', 'yaw'])
    df.to_csv("imu_data.csv", index=False)
    print("Dados coletados e salvos!")

# Geração de gráficos
def plot_data():
    df = pd.read_csv("imu_data.csv")
    
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(df['timestamp'], df['roll'], label="Roll", color='r')
    plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(df['timestamp'], df['pitch'], label="Pitch", color='g')
    plt.legend()
    
    plt.subplot(3, 1, 3)
    plt.plot(df['timestamp'], df['yaw'], label="Yaw", color='b')
    plt.legend()
    
    plt.xlabel("Tempo")
    plt.show()

# Executar
collect_data(duration=30)
plot_data()
