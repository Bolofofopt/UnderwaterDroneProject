import time
from brping import Ping1D

IP = "192.168.2.2"
PORT = 9090 

ping_sensor = Ping1D()

ping_sensor.connect_udp(IP, PORT)

if ping_sensor.initialize() is False:
    print("Failed to initialize Ping!")
    exit(1)


try:
    while True:
        data = ping_sensor.get_distance()
        if data:
            print("Distance: %s\tConfidence: %s%%" % (data["distance"], data["confidence"]))
        else:
            print("Failed to get distance data")
            # set the speed of sound to use for distance calculations to
        # 1450000 mm/s (1450 m/s)
        ping_sensor.set_speed_of_sound(1450000)
        time.sleep(1)  # Aguarde um segundo antes da próxima leitura

except KeyboardInterrupt:
    print("Encerrando leitura...")
    ping_sensor.close()
