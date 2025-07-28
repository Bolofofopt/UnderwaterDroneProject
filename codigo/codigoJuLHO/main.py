import threading
import time
import csv
from ROV360 import ROVsensors, ROVactuators
from pidController import PIDController

def csvLogPID():
    csv_file = open("log_PID.csv", mode="a", newline="")
    csv_writer = csv.writer(csv_file)

    # Sempre marca um novo bloco de execução
    csv_writer.writerow([])
    csv_writer.writerow(["timestamp", "depth_target", "depth_actual", "error",
                            "pid_output", "thrust_x", "thrust_y", "thrust_z",
                            "obstacle", "acao"])
    return csv_file, csv_writer

def csvLogSonar():
    sonar_file = open("log_Ping360.csv", mode="a", newline="")
    sonar_writer = csv.writer(sonar_file)

    sonar_writer.writerow([])
    sonar_writer.writerow(["timestamp", "angle_deg", "distance_m", "amplitude", "acao"])
    return sonar_file, sonar_writer



profundidadeAlvo = 1.3  # metros
DIST_MIN_OBSTACULO = 1.0
ANGLE_RANGE = (-30, 31, 5)
DIST_MIN_OBSTACULO = 2.0  # m
STEP_SIZE = 10
NUM_STEPS = int(400 / STEP_SIZE)


# === Flags compartilhadas ===
obstacleDetected = False
mensagem = ""
flagLock = threading.Lock()
missionRunning = True


def inicializarComponentes():
    sensors = ROVsensors()
    actuadores = ROVactuators()

    pidLateral = PIDController(kp=0.8, ki=0.0, kd=0.2)
    pidVertical = PIDController(kp=0.8, ki=0.0, kd=0.2)

    pingSensor = sensors.connectPing1D("192.168.2.2", 9090)
    ping360 = sensors.connectPing360("192.168.2.2", 9091)
    sensors.configPing360(
        ping360,
        gain=2,  # Nível de ganho (0 a 3)
        transmit_duration=25,  # Duração do pulso de transmissão em ms
        sample_period=80,  # Período de amostragem em ms
        number_of_samples=400  # Número de amostras
    )

    mavLink = sensors.connectMAVLINK("0.0.0.0", 14550)

    sensors.armROV(connectionMAVLINK=mavLink)
    return sensors, actuadores, pidLateral, pidVertical, pingSensor, ping360, mavLink

def getCurrentDepth(pingSensor):
    """Lê a profundidade atual do sensor Ping1D com verificação de None"""
    for _ in range(5):  # Tenta até 5 vezes
        data = sensors.get_ping1d_data(ping_sensor=pingSensor)
        if data and "distance" in data:
            return data["distance"] / 1000  # Convertendo mm para metros
    raise RuntimeError("Falha ao obter leitura válida do sensor Ping1D")

sensors, actuadores, pidLateral, pidVertical, pingSensor, ping360, mavLink = inicializarComponentes()
pidLateral.reset()
pidVertical.reset()

csv_file_PID, csv_writer_PID = csvLogPID()
csv_file_sonar, csv_writer_sonar = csvLogSonar()


# threading 1 PID
def manterProfundidade():
    print(f"A iniciar controlo de profundidade, alvo: {profundidadeAlvo} m")
    global obstacleDetected, mensagem, missionRunning
    print(f"A iniciar controlo de profundidade, alvo: {profundidadeAlvo} m")
    while missionRunning:
        try:
            currentDepth = getCurrentDepth(pingSensor)
        except RuntimeError:
            print("Falha na leitura do sensor Ping1D. Usando profundidade anterior.")
            continue
        error = profundidadeAlvo - currentDepth
        thrust = pidVertical.update(error)
        
        with flagLock:
            obstacle = obstacleDetected
            acao = mensagem

        if not obstacle:
            actuadores.set_thrust(
                thrust_z=thrust,  # Empuxo vertical PID
                thrust_y=0.0,     # Sem evasão lateral
                thrust_x=0.4,     # Frente
                connectionMAVLINK=mavLink
            )
            print(f"Profundidade atual: {currentDepth:.2f} m | Thrust: {thrust:.2f} | Direção: FRENTE")
        else:
            if acao == "ESQ":
                print("Desviar para ESQUERDA")
                actuadores.set_thrust(
                    thrust_z=thrust,
                    thrust_y=+0.2,   # esquerda
                    thrust_x=-0.2,
                    connectionMAVLINK=mavLink
                )
            elif acao == "DIR":
                print("Desviar para DIREITA")
                actuadores.set_thrust(
                    thrust_z=thrust,
                    thrust_y=-0.2,   # direita
                    thrust_x=-0.2,
                    connectionMAVLINK=mavLink
                )
            elif acao == "PARAR":
                print("Obstáculo muito próximo")
                actuadores.set_thrust(
                    thrust_z=thrust,
                    thrust_y=0.0,
                    thrust_x=-0.2,
                    connectionMAVLINK=mavLink
                )
                missionRunning = False #retirar?!
        timestamp = time.time()
        csv_writer_PID.writerow([
            timestamp,
            profundidadeAlvo,
            currentDepth,
            error,
            thrust,
            0.4 if not obstacle else 0.0,  # thrust_x
            0.0 if not obstacle else (0.2 if acao=="ESQ" else -0.2 if acao=="DIR" else 0.0),
            thrust,  # thrust_z
            obstacle,
            acao
        ])
        csv_file_PID.flush()
        time.sleep(0.01)

# === THREAD 2: SONAR LOOP ===
def sonar_loop():
    global obstacleDetected, mensagem
    while missionRunning:
        print("\n[Thread-Sonar] Varrendo Ping360...")
        for i in range(NUM_STEPS):
            angle_units = i * STEP_SIZE
            scan = sensors.get_ping360_data_scan(ping360, angle_units)
            if not scan:
                continue

            distance = scan['distance']
            angle_deg = scan['angle_deg']
            max_amp = scan['amplitude']

            amplitudes = scan['data']
            max_amp = max(amplitudes)
            max_idx = amplitudes.index(max_amp)
            meters_per_sample = 0.0015
            distance = max_idx * meters_per_sample

            angle_deg = angle_units * (360 / 400)
            
            if angle_deg > 180:
                angle_deg -= 360

            timestamp = time.time()
            csv_writer_sonar.writerow([
                timestamp,
                angle_deg,
                distance,
                max_amp,
                mensagem
            ])
            csv_file_sonar.flush()

            if distance <= DIST_MIN_OBSTACULO:
                print(f"Obstáculo a {distance:.2f} m no ângulo {angle_deg:.1f}°")
                # === Decide ação com base no ângulo ===
                if angle_deg >= -30 and angle_deg <= -5:
                    acao = "DIR"
                elif angle_deg >= 5 and angle_deg <= 30:
                    acao = "ESQ"
                elif distance < 0.5:  # muito perto
                    acao = "PARAR"
                else:
                    acao = "PARAR"

                with flagLock:
                    obstacleDetected = True
                    mensagem = acao

                time.sleep(0.5)  # espera antes de novo ping para não travar o loop

            else:
                # Se não há obstáculo, pode liberar
                with flagLock:
                    obstacleDetected = False
                    mensagem = ""

threading.Thread(target=manterProfundidade, daemon=True).start()
#threading.Thread(target=sonar_loop, daemon=True).start()

try:
    while missionRunning:
        time.sleep(1)
except KeyboardInterrupt:
    missionRunning = False
    print("Missão finalizada.")
finally:
    missionRunning = False
    csv_file_PID.close()
    csv_file_sonar.close()
    print("Arquivos CSV fechados.")
    sensors.disarmROV(connectionMAVLINK=mavLink)
    print("ROV desarmado.")


