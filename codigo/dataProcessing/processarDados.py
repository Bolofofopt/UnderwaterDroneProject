# código para processar dados de um ficheiro de texto (vindo do código para fazer
# o controle PID só da profundidade) e exportar para Excel
import re
import pandas as pd

# Caminho do ficheiro de texto com os dados (podes substituir pelo teu caminho)
input_file = "pidProfundidade.txt"
output_excel = "3recolha_PD_dados_processados.xlsx"

# Expressões regulares para capturar as informações
distance_re = re.compile(r"Distance:\s+(\d+)\s+Confidence:\s+(\d+)%")
control_re = re.compile(r"Alvo:\s+([\d.]+)\s+m\s+\|\s+Atual:\s+([\d.]+)\s+m\s+\|\s+Thrust:\s+(-?[\d.]+)")

# Leitura das linhas do ficheiro
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Processamento ajustado para ignorar linhas com "Thrust X, Y, Z"
dados = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    match1 = distance_re.match(line)
    if match1:
        distance = int(match1.group(1))
        confidence = int(match1.group(2))

        # Procurar próxima linha válida com os dados de controlo
        j = i + 1
        while j < len(lines):
            line2 = lines[j].strip()
            if "Thrust X" in line2:
                j += 1  # Ignora esta linha e continua a procurar
                continue
            match2 = control_re.match(line2)
            if match2:
                alvo = float(match2.group(1))
                atual = float(match2.group(2))
                thrust = float(match2.group(3))

                dados.append({
                    "Distance (mm)": distance,
                    "Confidence (%)": confidence,
                    "Alvo (m)": alvo,
                    "Atual (m)": atual,
                    "Thrust": thrust
                })
                i = j  # Atualiza o índice principal
                break
            else:
                j += 1
        i = j + 1
    else:
        i += 1


# Criar DataFrame e exportar para Excel
df = pd.DataFrame(dados)
df.to_excel(output_excel, index=False)
print(f"Exportado para: {output_excel}")
