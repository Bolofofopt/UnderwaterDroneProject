# BlueRovProject
<p align="center"><img width="100%" src="img/ENIDH.png" /></p>


--------------------------------------------------------------------------------

This repository shows my projects done with the BlueRov2 submarine.

Done when studing in Escola Náutica Infante Dom Henrique.

<br/>

### Skills melhoradas / aprendidas:
      - Gestão de Equipa
      - Desenvolvimento de software (Python)
      - Navegação baseada em terreno (TBN)
      - Navegação por Inércia (INS)
      - Controlador PID
      - MAVLink
      - Telemetria 
      - Manutenção do ROV
### Projetos desenvolvidos
      - Analise de telemetria sensorial
      - Manter a profundidade (PID controler)
      - INS autónomo 

# Descrição do projeto/tecnologias
### Métodos de comunicação
##### PyMavLink
PyMavLink foi utilizado para estabelecer uma conexão com o ROV via Script de Python. Pymavlink é uma biblioteca de processamento de mensagens MAVLink de baixo nível e de uso geral.

Para utilizar MAVLink primeiro ativou-se no BlueOS um MAVLinkendpoint.
O MAVLinkendpoint usado foi o GCSServerLink (Ground Control Station Server Link). É um endpoint UDP que permite um GCS (Ground Control Station) conectar ao veículo via protocolo MAVLink. O GCS envia comandos para o ROV que solicitam dados de telemetria, recebendo em troca os dados pedidos, estados do sistema, dados dos sensores puro ou dados dos #sensores previamente tratados. Por ser um Endpoint UDP foi preciso fazer validação dos dados antes de enviar para o algoritmo.

##### Comunicação serie
ComunicaçãoSerie foi utilizada para conectar aos seguintes sensores:
- Ping Sonar Altimeter and Echosounder
- Ping360 Scanning Imaging Sonar

Para descobrir qual o endereço dos sensores utilizou-se o PingViewer, pois ele faz uma busca da rede e dá o endereço e a porta dos sensores Ping disponíveis, porém também se pode usar o software BlueOS na aba dos sensores.

## Análise de telemetria & Manter profundidade
A análise de telemetria dos sensores é essencial para saber se é necessário aplicar um filtro nos dados que estão a ser recebidos dos sensores. O sensor sob analise é o Ping Sonar Altimeter and Echosounder. Para fazer a análise desse sensor foi preciso manter a profundidade do ROV, para o fazer utilizou-se um controladorPID.

### Controlador PID (Proporcional integral derivativo)
Um controladorPID, na área de controlo, é um algoritmo de feedback muito usado pela sua versatilidade, facilidade de implementação e resiliência durante a sua utilização. Combina três tipos de ações, a ação proporcional (Kp), ação integral (Ki) e ação derivativa (Kd). Para alcançar um melhor desempenho do controlador PID é necessário ajustar esses valores, esse ajuste pode ser feito através do método tentativa e erro até o controlador alcançar um bom comportamento, ou, através de inteligência artificial ou algoritmos de otimização para encontrar os melhores parâmetros durante a utilização do controlador, criando um ambiente dinâmico. Apesar de ser versátil e fácil de implementar existem desafios associados, como por exemplo, ruídos no sistema (que será abordado a seguir). Onde u(t) é o sinal de saída,

$$ u(t) = K_pe(t) + K_i \int_0^t e(\tau)d\tau + K_p \frac{de(t)}{dt} $$

Transformada de Laplace: (s = frequência complexa)
$$ L_s =  K_p+K_i/s+K_ds $$

Como a mudança de cada parâmetro afeta a performance:
![[Pasted image 20250512113629.png]]

No primeiro teste o proporcional estava muito elevado. Corrigindo isso conseguimos analisar a segunda recolha de telemetria.
<p align="center"><img width="100%" src="img/segundaRecolha.png" /></p>

#### Conclusões PID

# Visão (Processamento de Imagem)



# ROV
BlueROV2 é o drone subaquático da BlueRobotics.

Tem os seguintes sensores: 
- Ping Sonar Altimeter and Echosounder
- Ping360 Scanning Imaging Sonar
- Newton Subsea Gripper (Garra)
- Sensores IMUs
- Sensor de pressão
- Câmera

