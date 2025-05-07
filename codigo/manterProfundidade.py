import time
from ROV import ROVsensors, ROVactuators

# Inicializações
sensors = ROVsensors()
actuators = ROVactuators()

pingSensor = sensors.connectPing1D("192.168.2.2", 9090)
mavLink = sensors.connectMAVLINK("0.0.0.0", 14550)

# Constantes PID
Kp = 1.0
Ki = 0.0
Kd = 0.0

# Variáveis do PID
prev_error = 0.0
integral = 0.0

def get_current_depth():
    """Lê a profundidade atual do sensor Ping1D com verificação de None"""
    for _ in range(5):  # Tenta até 5 vezes
        data = sensors.get_ping1d_data(ping_sensor=pingSensor)
        if data and "distance" in data:
            return data["distance"] / 1000  # Convertendo mm para metros
        time.sleep(0.01)
    raise RuntimeError("Falha ao obter leitura válida do sensor Ping1D")

def depth_hold(target_depth):
    """Mantém profundidade usando controle PID"""
    global prev_error, integral

    print(f"Iniciando controle de profundidade para: {target_depth:.2f} m")

    try:
        while True:
            current_depth = get_current_depth()
            error = target_depth - current_depth
            integral += error
            derivative = error - prev_error
            prev_error = error

            # Cálculo do sinal de controle (thrust)
            thrust = (Kp * error) + (Ki * integral) + (Kd * derivative)
            thrust = max(min(thrust, 2), 0)  # Limita entre -1 e 1

            # Envia comando de empuxo
            actuators.set_thrust(thrust, connectionMAVLINK=mavLink)

            # Debug
            print(f"Alvo: {target_depth:.2f} m | Atual: {current_depth:.2f} m | Thrust: {thrust:.2f}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Controle de profundidade interrompido pelo usuário.")

def profundidadeInicial():
    """Lê a profundidade inicial para ser usada como referência"""
    profundidade = get_current_depth()
    print(f"Profundidade Inicial: {profundidade:.2f} m")
    return profundidade

if __name__ == "__main__":
    profundidade_alvo = profundidadeInicial()
    depth_hold(2)
