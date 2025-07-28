import vlc  # type: ignore 
import os
import time
from pymavlink import mavutil # type: ignore
from brping import Ping1D, Ping360 # type: ignore

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

    def connectPing360(self, IP, PORT):
        """_summary_

        Args:
            IP (str): 192.168.2.2
            PORT (int): 9091 ?

        Returns:
            connection to Ping360
        """
        ping360 = Ping360()
        print(f"Connecting to Ping360 on {IP}:{PORT}...")
        ping360.connect_udp('192.168.2.2', 9092)
        if ping360.initialize() is False:
            print("Failed to initialize Ping360!")
            exit(1)

        print("Ping360 conectado!")
        return ping360

    def configPing360(self, ping360, gain=2, transmit_duration=20, sample_period=80, number_of_samples=200):
        """Configura o Ping360 
        Args:
            ping360 (Ping360): Instância do Ping360
            gain (int): Nível de ganho (0 a 3)
            transmit_duration (int): Duração do pulso de transmissão em microssegundos
            sample_period (int): Período de amostragem em nanossegundos
            number_of_samples (int): Número de amostras a serem coletadas
        
        """
        ping360.set_gain_setting(gain) 
        ping360.set_transmit_duration(transmit_duration)
        ping360.set_sample_period(sample_period)         # em nanosegundos
        ping360.set_number_of_samples(number_of_samples)
        
        
    def get_ping360_data_scan(self, ping360, angle_units):
        """
        Realiza varredura com Ping360 e retorna dados validados.
        """
        try:
            ping360.control_transducer(
                angle=angle_units,
                mode=1,
                gain_setting=2,
                transmit_duration=25,
                sample_period=80,
                transmit_frequency=40000,
                number_of_samples=400,
                transmit=1,
                reserved=0
            )

            # Aguarda mensagem do tipo 'ping360' (Message ID 130)
            for _ in range(10):  # tenta até 10 vezes
                msg = ping360.receive_message()
                if msg and msg.message_id == 130 and hasattr(msg, 'data'):
                    amplitudes = list(msg.data)
                    max_amp = max(amplitudes)
                    max_idx = amplitudes.index(max_amp)

                    meters_per_sample = 0.0015
                    distance = max_idx * meters_per_sample

                    angle_deg = angle_units * (360 / 400)
                    if angle_deg > 180:
                        angle_deg -= 360

                    return {
                        "angle_deg": angle_deg,
                        "distance": distance,
                        "amplitude": max_amp,
                        "data": amplitudes
                    }
            print("Nenhum ping360 recebido dentro da janela de tempo.")
            return None

        except Exception as e:
            print(f"Erro durante varredura Ping360: {e}")
            return None


    def get_ping360_data_all_angles(self, ping360, NUM_STEPS, STEP_SIZE, DIST_MIN_OBSTACULO):
        """Obtém dados do Ping360 para todos os ângulos de 0 a 360 graus.
        
        Args:
            ping360 (Ping360): Instância do Ping360
        
        Returns:
            list: Lista de dicionários com dados de cada ângulo
        """
        for i in range(NUM_STEPS):
            angle_units = i * STEP_SIZE   # Ex: 0, 10, 20, ..., 390
            ping360.transducer(angle_units, 0, 400)
            scan = ping360.get_message()
            
            amplitudes = scan['data']
            max_amp = max(amplitudes)
            max_idx = amplitudes.index(max_amp)

            # Converter para metros (aproximadamente)
            meters_per_sample = 0.0015  # ajustável conforme config
            distance = max_idx * meters_per_sample

            # Converter unidades para graus
            angle_degrees = angle_units * (360 / 400)

            if distance <= DIST_MIN_OBSTACULO:
                print(f"Obstáculo a {distance:.2f} m no ângulo {angle_degrees:.1f}° (amp={max_amp})")
            else:
                print(f"Sem obstáculo (ângulo {angle_degrees:.1f}°, distância={distance:.2f} m)")


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
        connectionMAVLINK.set_mode('MANUAL')
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
        connectionMAVLINK.set_mode('MANUAL')
        print("Arming the ROV...")
        connectionMAVLINK.mav.command_long_send(
            connectionMAVLINK.target_system,
            connectionMAVLINK.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            1,  # arm
            0, 0, 0, 0, 0, 0
        )
        connectionMAVLINK.set_mode('MANUAL')

        #connectionMAVLINK.set_mode('STABILIZE')

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

        print(f"Thrust X: {x_mav}, Y: {y_mav}, Z: {z_mav}")
        connectionMAVLINK.mav.manual_control_send(
            connectionMAVLINK.target_system,
            x_mav, y_mav, z_mav,
            0, 0  # yaw e botões
        )

if __name__ == "__main__":
    sensors = ROVsensors()
    actuatores = ROVactuators()
