# depth_hold.py
import time
from ROVlateralvertical import ROVsensors, ROVactuators
from pidController import PIDController

# Inicializa sensores e atuadores
sensors = ROVsensors()
actuators = ROVactuators()

pingSensor = sensors.connectPing1D("192.168.2.2", 9090)
mavLink = sensors.connectMAVLINK("0.0.0.0", 14550)
sensors.armROV(connectionMAVLINK=mavLink)

# Instância do controlador PID
pid = PIDController(kp=1.0, ki=0.0, kd=0.0)

def get_current_depth():
    """Lê a profundidade atual do sensor Ping1D com verificação de None"""
    for _ in range(5):  # Tenta até 5 vezes
        data = sensors.get_ping1d_data(ping_sensor=pingSensor)
        if data and "distance" in data:
            return data["distance"] / 1000  # Convertendo mm para metros
    raise RuntimeError("Falha ao obter leitura válida do sensor Ping1D")

def depth_hold(target_depth):
    pid.reset()
    print(f"Iniciando controle de profundidade para: {target_depth:.2f} m")

    try:
        while True:
            current_depth = get_current_depth()
            error = target_depth - current_depth
            thrust = pid.update(error)

            actuators.set_thrust(
                thrust_z=thrust,  # Empuxo vertical
                thrust_y=0.0,     # Empuxo lateral (não usado)
                thrust_x=0.0,     # Empuxo para frente (não usado)
                connectionMAVLINK=mavLink
            )
            
            print(f"Alvo: {target_depth:.2f} m | Atual: {current_depth:.2f} m | Thrust: {thrust:.2f}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Controle de profundidade interrompido pelo usuário.")
        sensors.disarmROV(connectionMAVLINK=mavLink)

def profundidadeInicial():
    """Lê a profundidade inicial para ser usada como referência"""
    profundidade = get_current_depth()
    print(f"Profundidade Inicial: {profundidade:.2f} m")
    return profundidade

if __name__ == "__main__":
    #profundidade_alvo = profundidadeInicial()
    depth_hold(1.5)
