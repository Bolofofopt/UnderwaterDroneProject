import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata # type: ignore
from scipy.optimize import minimize # type: ignore


def criarEixo():
    x_lim, y_lim = 100, 100

    boias = np.array([[10, 90], [30, 50], [70, 20]])
    rov_real = np.random.rand(1, 2) * [x_lim, y_lim]

    distancias = np.sqrt(np.sum((boias - rov_real)**2, axis=1))

    ruido = np.random.normal(0, 2, size=distancias.shape)  # Média 0, desvio padrão 2
    distancias_com_ruido = distancias + ruido

    def erro(estimativa_rov):
        return np.sum((np.sqrt(np.sum((boias - estimativa_rov)**2, axis=1)) - distancias_com_ruido)**2)
    
    resultado = minimize(erro, x0=[50, 50], bounds=[(0, x_lim), (0, y_lim)])
    rov_estimado = resultado.x
    plt.figure(figsize=(8, 8))
    plt.grid(True)
    plt.xlim(0, x_lim)
    plt.ylim(0, y_lim)
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')

    plt.scatter(boias[:, 0], boias[:, 1], color='red', label='Boias')
    plt.scatter(rov_real[:, 0], rov_real[:, 1], color='blue', label='ROV (Real)')
    plt.scatter(rov_estimado[0], rov_estimado[1], color='green', label='ROV (Estimado)')

    for i, (x, y) in enumerate(boias):
        plt.text(x, y, f'{distancias_com_ruido[i]:.2f}', color='green', fontsize=10)

    plt.legend()
    plt.title("Posições das Boias e do ROV")
    plt.show()


criarEixo()