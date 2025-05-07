from ROV import ROVsensors

sensors = ROVsensors()



ping1d = sensors.connectPing1D(IP = "192.168.2.2", PORT = 9090)
sensors.get_ping1d_data(ping_sensor=ping1d)

mauvlinkConnection = sensors.connectMAVLINK(IP="0.0.0.0", PORT = 14550)
sensors.get_pitch_roll(connectionMAVLINK=mauvlinkConnection)

