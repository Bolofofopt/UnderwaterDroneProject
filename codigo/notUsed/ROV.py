from pymavlink import mavutil # type: ignore
from brping import Ping1D # type: ignore


class ROVsensors():
    def connectPing1D(self, IP, PORT):
        """_summary_

        Args:
            IP (str): 192.168.2.2
            PORT (int): 9090

        Returns:
            connection to PingSensor
        """

        ping_sensor = Ping1D()
        ping_sensor.connect_udp(IP, PORT)
        if ping_sensor.initialize() is False:
            print("Failed to initialize Ping!")
            exit(1)
        return ping_sensor

    def get_ping1d_data(self, ping_sensor):
        data = ping_sensor.get_distance()
        
        #acho que é preciso dividir por 1000 para ter a distância em metros
        if data:
            #data = data / 1000 #converte de mm para m 
            print("Distance: %s\tConfidence: %s%%" % (data["distance"], data["confidence"]))
        else:
            print("Failed to get distance data")
        ping_sensor.set_speed_of_sound(1450000)
        return data
        
    def closePing1D(self, ping_sensor):
        ping_sensor.close()

    def connectMAVLINK(self, IP, PORT):
        """_summary_

        Args:
            IP (str): "0.0.0.0"
            PORT (int): 14550

        Returns:
            connectionMAVLINK
        """
        connectionMAVLINK = mavutil.mavlink_connection(f"udp:{IP}:{PORT}")
        connectionMAVLINK.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (connectionMAVLINK.target_system, connectionMAVLINK.target_component))
        return connectionMAVLINK

    def get_pitch_roll(self, connectionMAVLINK):
        connectionMAVLINK.wait_heartbeat()
        print("Connected to BlueROV2!")
        msg = connectionMAVLINK.recv_match(type='ATTITUDE', blocking=True)
        if msg:
            attitude_data = {
                "timestamp": msg.time_boot_ms,
                "roll": msg.roll,    # In radians
                "pitch": msg.pitch,  # In radians
                "yaw": msg.yaw       # In radians
            }
            print(f"Processed IMU Data: {attitude_data}")
            return attitude_data


class ROVactuators():
    def set_thrust(self, thrust, connectionMAVLINK):
        """_summary_

        Args:
            thrust (float): RESULTADO DO PID
            connectionMAVLINK: MAVLINK connection object
        
            manual_control_send(
            target_system,
            x, y, z, r, buttons) 
                x → movimento para frente/trás (surge)
                y → movimento lateral esquerda/direita (sway)
                z → aceleração vertical (heave)
                r → yaw rate (giro no eixo Z)
                buttons → comandos adicionais (geralmente 0)
        """
        thrust = max(min(thrust, 0.5), -0.5)+0.5  # Limita entre 0(reverse) e 1(full thrust)
        if not -1 <= thrust <= 1:
            raise ValueError("Thrust out of bounds!")
        connectionMAVLINK.mav.manual_control_send(
            connectionMAVLINK.target_system,
            0, 0, int(thrust * 1000),  # Throttle (-1000 to 1000)
            0, 0)

if __name__ == "__main__":
    sensors = ROVsensors()
    actuatores = ROVactuators()
