# Omnitrix Run - V8

## Desenvolvedores
- Nome completo: Igor Pereira de Medeiros
- RA: 1139603
- Nome completo: Camila Bueno
- RA: PREENCHER

> Antes da entrega, preencham os nomes completos e os RAs dos dois integrantes. Esses dados nao foram colocados para evitar inventar informacoes.

## Historia
Um jovem heroi entra em uma selva tomada por criaturas perigosas. Com um dispositivo alienigena, ele pode assumir duas formas: Chamas, que dispara bolas de fogo, e Bola de Canhao, que avanca rolando contra os inimigos. Ratinhos correm pela trilha e morcegos mergulham do alto, enquanto um vilao observa a batalha montado em uma criatura anfibia. O objetivo e sobreviver, derrotar os inimigos e conquistar a maior pontuacao.

## Tecnologias utilizadas
- Python 3
- Pygame Community Edition (`pygame-ce`)
- `pyttsx3` para fala sintetizada
- Git e GitHub para controle de versao

## Como instalar e executar no Windows
1. Instale Python 3.10 ou superior.
2. Extraia todos os arquivos para uma pasta.
3. Abra o CMD dentro da pasta que contem `main.py` e `requirements.txt`.
4. Instale as dependencias: `py -m pip install -r requirements.txt`.
5. Execute o jogo: `py main.py`.

Se o comando `py` nao funcionar, use `python` no lugar dele.

## Controles
- A/D ou setas esquerda/direita: mover no eixo X.
- SHIFT: correr.
- W ou seta para cima: pular.
- S ou seta para baixo: agachar.
- G: abrir/fechar o menu do Omnitrix.
- 1: transformar em Chamas.
- 2: transformar em Bola de Canhao.
- 0: voltar ao heroi (com o menu aberto).
- Z ou botao esquerdo do mouse: atacar.
- SPACE: pausar/continuar.
- ESC: fechar o jogo.

## Funcionalidades
- Tela inicial tematizada, com campo de nome, botao interativo e ranking Top 5.
- Tela de boas-vindas com nome do jogador, explicacao da mecanica e um unico botao para iniciar.
- A tela de boas-vindas mostra os melhores resultados com data e hora.
- O jogo tem tres vidas, mostradas por tres coracoes.
- Chamas dispara bolas de fogo e Bola de Canhao ataca rolando.
- Os ataques possuem intervalo de recarga de 1,5 segundo.
- Ratinhos e morcegos surgem durante a partida e ficam mais rapidos e numerosos com o tempo.
- A personagem pode se mover no eixo X e pular no eixo Y, sem movimento diagonal.
- Um objeto decorativo se movimenta de forma aleatoria, sem interagir com o jogador.
- Um circulo amarelo no canto da tela pulsa lentamente.
- A tecla SPACE pausa o jogo e exibe PAUSE no centro.
- A mensagem `Press Space to Pause Game.` aparece discretamente durante a partida.
- O jogo registra nome, pontuacao, data e hora no arquivo `log.dat` (formato HH:MM:SS).
- A tela de fim de jogo mostra o competidor com maior pontuacao.
- `pyttsx3` e utilizado na tela de boas-vindas.
- ESC fecha o jogo completamente.

## Animacoes da V8
- Chamas: quadros parados e correndo padronizados pela altura visivel, para nao aumentar/diminuir ao trocar de estado.
- Bola de Canhao: um unico modelo visual pixel-art e animacoes separadas de repouso, caminhada, corrida, pulo, agachamento e ataque. Todos os estados usam o mesmo conjunto-base de sprites.

## Audio
Os arquivos WAV desta versao foram compostos e sintetizados originalmente para o projeto: musica de fundo, transformacao, disparo, soco, impacto, pontuacao, morte, pulo, rolamento e interface. Todos ficam dentro de `bases/sons/`.

Consulte `bases/sons/FONTES_AUDIO.txt` para as referencias externas pesquisadas e informacoes de licenca.

## Estrutura principal
- `main.py`: codigo principal do jogo.
- `Recursos/trabalho.py`: funcoes auxiliares importadas pelo programa.
- `bases/imagens/`: capa, cenario, personagens, inimigos, animacoes e efeitos visuais.
- `bases/sons/`: musica e efeitos sonoros.
- `bases/fontes/`: fonte usada na interface.
- `bases/icones/`: icone do projeto.
- `log.dat`: historico das partidas, no formato `nome|pontuacao|data|hora`.

O codigo foi mantido em nivel introdutorio, usando funcoes, variaveis, listas, condicoes, repeticoes e eventos do Pygame, sem classes ou programacao orientada a objetos.

## Gerar o executavel
O PDF solicita a geracao com `python setup.py build` e a inclusao do executavel no commit final.

1. Instale o empacotador: `py -m pip install -r requirements-build.txt`.
2. Execute: `python setup.py build` (ou `py setup.py build` no Windows).
3. O executavel e os arquivos de suporte serao criados na pasta `build/`.

## Conferencia da entrega pelo PDF
- [ ] Conferir que o repositorio tem pelo menos cinco commits descritivos.
- [ ] Preencher nomes completos e RAs dos dois desenvolvedores.
- [ ] Compartilhar com o professor `marcos.santos@atitus.edu.br` ou `profmarcossantos`.
- [ ] Adicionar o colega como colaborador e pedir que ele faca um commit no repositorio.
- [ ] Gerar o executavel com `python setup.py build` e inclui-lo no commit final.
