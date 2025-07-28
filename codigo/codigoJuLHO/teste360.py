from brping import Ping360

ping360 = Ping360()
ping360.connect_udp("192.168.2.2", 9092)
ping360.initialize()
info = ping360.get_device_data()
print(info)


print("Ping360 conectado!")

# Testar valores para transmit_frequency:
test_freqs = [48000, 40000, 30000, 10000, 48, 0]
for freq in [0, 1, 10, 48000, 65535]:
    try:
        print(f"Testando transmit_frequency = {freq}")
        ping360.control_transducer(
            angle=0,
            mode=1,
            gain_setting=2,
            transmit_duration=25,
            sample_period=80,
            transmit_frequency=freq,
            number_of_samples=400,
            transmit=1,
            reserved=0
        )
        print("Comando enviado com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
