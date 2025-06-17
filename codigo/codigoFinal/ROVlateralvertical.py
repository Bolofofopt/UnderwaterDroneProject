import vlc  # type: ignore 
import os
import time
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

    def connectMAVLINK(self, IP, PORT):
        """_summary_

        Args:
            IP (str): "0.0.0.0"
            PORT (int): 14550

        Returns:
            connectionMAVLINK
        """
        print(f"Connecting to MAVLink on {IP}:{PORT}...")
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

    def connectCamera(self, osDirectory, SDPfile):
        """Conecta à câmera usando VLC e retorna o player.
        Esta função adiciona o diretório de DLLs do VLC e cria uma instância do player VLC.

        Args:
            osDirectory (r""): r"C:\Program Files\VideoLAN\VLC"
            SDPfile (r""): C:\path\camerarov.sdp 

        Returns:
            _type_: player VLC
        """
        # os.add_dll_directory(osDirectory)
        os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
        options = ["--network-caching=100", "--drop-late-frames", "--skip-frames"]
        instance = vlc.Instance(*options)
        # media = instance.media_new(SDPfile)
        media = instance.media_new(
            r"C:\Users\henri\Documents\Articles-Documents\Documents\Projects\Faculdade\ProjetoSubmarino\codigo\codigoFinal\camararov.sdp"
        )
        player = instance.media_player_new()
        player.set_media(media)
        player.play()
        time.sleep(2)
        return player

    def release_camera(self):
        """Libera o recurso da câmera"""
        if self.cap:
            self.cap.release()
            self.cap = None

    def armROV(self, connectionMAVLINK):
        """Arma o ROV para iniciar a operação.
        
        Args:
            connectionMAVLINK: MAVLINK connection object
        """
        print("Arming the ROV...")
        connectionMAVLINK.mav.command_long_send(
            connectionMAVLINK.target_system,
            connectionMAVLINK.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            1,  # arm
            0, 0, 0, 0, 0, 0
        )

    def disarmROV(self, connectionMAVLINK):
        """Desarma o ROV para parar a operação.
        
        Args:
            connectionMAVLINK: MAVLINK connection object
        """
        print("Disarming the ROV...")
        connectionMAVLINK.mav.command_long_send(
            connectionMAVLINK.target_system,
            connectionMAVLINK.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            0,  # disarm
            0, 0, 0, 0, 0, 0
        )

class ROVactuators():
    def set_thrust(self, thrust_x, thrust_y, thrust_z, connectionMAVLINK):
        """Controla movimento vertical e lateral.
            Args:
                thrust_z (float): valor de PID para vertical (-0.5 a 0.5)
                thrust_y (float): valor de PID para lateral (-0.5 a 0.5)
                thrust_x (float): valor fixo ou PID para frente/trás (-1.0 a 1.0)
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
        
        thrust_x = max(min(thrust_x, 1.0), -1.0)  # frente/trás é centrado em 0
        thrust_y = max(min(thrust_y, 0.5), -0.5)  # lateral é centrado em 0
        thrust_z = max(min(thrust_z, 0.5), -0.5) + 0.5 # centrado em 0.5 para heave
        
        # Converter para escala MAVLink (-1000 a 1000)
        x_mav = int(thrust_x * 1000)
        y_mav = int(thrust_y * 1000)
        z_mav = int(thrust_z * 1000)

        connectionMAVLINK.mav.manual_control_send(
            connectionMAVLINK.target_system,
            x_mav, y_mav, z_mav,
            0, 0  # yaw e botões
        )

if __name__ == "__main__":
    sensors = ROVsensors()
    actuatores = ROVactuators()
