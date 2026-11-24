# Omnitrix Run

## Desenvolvedores
- Nome Igor Pereira
- RA: 1139603
- Nome completo: Camila Bueno
- RA: 1140231

## História
Um jovem portador de um dispositivo alienígena precisa atravessar uma zona perigosa, destruindo inimigos enquanto tenta conseguir a maior pontuação possível. O jogo usa uma temática de transformação alienígena inspirada no estilo de jogos clássicos de heróis, com identidade visual própria.

## Tecnologias utilizadas
- Python
- Pygame
- pyttsx3
- Git e GitHub

## Como executar
1. Instale Python.
2. Instale as dependências:
   `py -m pip install -r requirements.txt`
3. Execute:
   `python main.py`

## Estrutura
- `main.py`: arquivo principal do jogo.
- `Recursos/trabalho.py`: contém uma função útil criada separadamente e importada pelo principal.
- `bases/`: imagens, sons, fontes e ícones. A imagem `bases/imagens/capa.png` aparece na primeira tela do jogo.
- `log.dat`: registro das partidas.
- `bases/imagens/animacoes/`: frames PNG separados para caminhar, correr, atacar, pular, rolar, morrer e transformar.
- `bases/imagens/spritesheet_referencia.png`: spritesheet original usada para separar os frames.

## Controles
- A / D ou setas esquerda/direita: movimentar no eixo X.
- Shift: correr.
- Z: atacar/disparar.
- Space: pausar/continuar.
- ESC: fechar completamente.

## Versão 2 - Animações
- Foram separados 40 frames em PNG, organizados por movimento.
- Caminhada e corrida já estão ligadas ao controle do jogador.
- A tecla Shift ativa a corrida; A/D ou as setas movimentam no eixo X.
- A tecla Z dispara e exibe a animação de ataque.
- Os frames de pulo, rolamento, morte e transformação estão organizados para integração nas próximas etapas.
- O código continua sem classes.

## Requisitos da atividade
O projeto foi estruturado para atender aos itens da atividade de Pygame, incluindo tela de nome, tela de boas-vindas, pausa, objeto decorativo aleatório, sol pulsante, log, maior pontuação, uso de pyttsx3 e organização dos assets em `bases/`.
