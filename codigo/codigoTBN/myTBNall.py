import numpy as np
import matplotlib.pyplot as plt
import random
import time
from scipy.interpolate import griddata # type: ignore

from manterProfundidade import manterPru
from ROV import ROVsensors


h = 0
contadorPNG = 0

"""Preciso de código para saber qual a distância a que estou do nível da água.
+
Código para saber a distância ao solo
=
Ambos resultados estarem nas imagens TBN
"""




#def lerIMU():

#PRIMEIRO
def manterPrufundidadeCALL():
    if(h == 0):
        profundidadeInicial = ROVsensors.get_altimeter_data()
        h = 1
        print("\nProfundidade atual = ", profundidadeInicial)
    
    manterPru(profundidadeInicial)
    print("profundidade atual vs profundidade inicial\n", ROVsensors.get_altimeter_data, "vs", profundidadeInicial)
    

def guardarPNG(contadorPNG):
    nomePNG = f"{contadorPNG:02d}_fig.png"
    contadorPNG += 1
    nomePNG = (r"C:\Users\henri\Documents\Articles-Documents\Documents\Projects\Faculdade\ProjetoSubmarino\TBNtestePNG"
    + "\\" + str(contadorPNG) + nomePNG)
    print(nomePNG)
    plt.savefig(nomePNG, bbox_inches='tight')
    return contadorPNG

while(True):
    def generate_tbn_map(samples=100):
        """Generates a terrain-based navigation map from sensor data."""
        x_data, y_data, depth_data = [], [], []

        print("Collecting sensor data...")
        
        for _ in range(samples):
            sensor_reading = ROVsensors.get_tbn_sensor_data()
            x_data.append(sensor_reading["x"])
            y_data.append(sensor_reading["y"])
            depth_data.append(sensor_reading["depth"])
            time.sleep(0.05) 

        print("Sensor data collection complete!")

        # Separar a grelha 2D
        grid_x, grid_y = np.meshgrid(
            np.linspace(min(x_data), max(x_data), 100),
            np.linspace(min(y_data), max(y_data), 100)
        )
        grid_depth = griddata((x_data, y_data), depth_data, (grid_x, grid_y), method="cubic")


        """Objetivo é o plt.scatter marcar onde é que, no plano x,y o sensor recolheu os dados,
        pra isso acontecer bem é preciso os x estarem muito próximos uns dos outros por não haver MBE e SSS
        """
        #colocar a posição inicial do ROV no eixo 
        plt.figure(figsize=(8, 6))
        contour = plt.contourf(grid_x, grid_y, grid_depth, cmap="viridis", levels=15)
        plt.colorbar(contour, label="Depth (m)")
        plt.scatter(x_data, y_data, c="red", marker="x", label="Sensor Readings")
        plt.xlabel("X Position (m)")
        plt.ylabel("Y Position (m)")
        plt.title("Terrain-Based Navigation (TBN) Map")
        plt.legend()
        #plt.show()

    generate_tbn_map()
    contadorPNG = guardarPNG(contadorPNG)

