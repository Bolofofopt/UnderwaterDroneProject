from PIDcontroler import PIDController
from ROV import ROVsensors

sensors = ROVsensors()
pid = PIDController(kd=3, kp=5, ki=0.1)

IPPING = "192.168.2.2"
PORTPING = 9090
IPMAV = "0.0.0.0"
PORTMAV = 14550

pingSensor = sensors.connectPing1D(IP=IPPING, PORT=PORTPING)
mavLINK = sensors.connectMAVLINK(IP=IPMAV, PORT=PORTMAV)



def profundidadeInicial():
    profunPretendida = sensors.get_ping1d_data(ping_sensor=pingSensor)
    if profunPretendida is None:
        print("Erro: Profundidade Null.")
        while(profunPretendida	== None):
            profunPretendida = sensors.get_ping1d_data(ping_sensor=pingSensor)
    print(f"Profundidade Inicial: {profunPretendida:.2f}m")
    return profunPretendida

profunPretendida = profundidadeInicial()
while(True):
    profunAtual = sensors.get_ping1d_data(ping_sensor=pingSensor)
    if profunAtual is None:
        print("Erro: Profundidade Null.")
        while(profunAtual	== None):
            profunAtual = sensors.get_ping1d_data(ping_sensor=pingSensor)
    print(f"Profundidade Atual: {profunAtual:.2f}m")

    thrust = pid.compute(profunPretendida, profunAtual)
    
    sensors.set_thrust(thrust=thrust, connectionMAVLINK=mavLINK)
    
    pitch, roll = sensors.get_pitch_roll(mavLINK)

    print(f"Depth: {sensors.get_ping1d_data(ping_sensor=pingSensor):.2f}m, Target: {profunPretendida:.2f}m, Thrust: {thrust:.2f}")
    print(f"Pitch: {pitch:.2f}°, Roll: {roll:.2f}")