import pandas as pd
import matplotlib.pyplot as plt

# === Configurações gerais ===
csv_file = 'pid_output_log.csv'

# === Ler o CSV ===
df = pd.read_csv(csv_file)

# Converter coluna de tempo (se não estiver já como float)
df['Elapsed_Time(s)'] = df['Elapsed_Time(s)'].astype(float)

# === Plot 1: Posição do centroide ao longo do tempo ===
plt.figure(figsize=(10, 5))
plt.plot(df['Elapsed_Time(s)'], df['Centroide_X'], label='Centroide X', color='red')
plt.plot(df['Elapsed_Time(s)'], df['Centroide_Y'], label='Centroide Y', color='blue')
plt.xlabel('Tempo (s)')
plt.ylabel('Posição do Centroide (px)')
plt.title('Centroide ao longo do tempo')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === Plot 2: Erro do centroide ===
plt.figure(figsize=(10, 5))
plt.plot(df['Elapsed_Time(s)'], df['Erro_X'], label='Erro X', color='orange')
plt.plot(df['Elapsed_Time(s)'], df['Erro_Y'], label='Erro Y', color='purple')
plt.xlabel('Tempo (s)')
plt.ylabel('Erro (px)')
plt.title('Erro do Centroide ao longo do tempo')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === Plot 3: Saída dos controladores PID ===
plt.figure(figsize=(10, 5))
plt.plot(df['Elapsed_Time(s)'], df['PID_Lateral_Output'], label='Saída PID Lateral', color='green')
plt.plot(df['Elapsed_Time(s)'], df['PID_Vertical_Output'], label='Saída PID Vertical', color='brown')
plt.xlabel('Tempo (s)')
plt.ylabel('Saída PID')
plt.title('Saídas dos controladores PID ao longo do tempo')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
