# Omnitrix Run - V11

## Desenvolvedores
- Nome completo: Igor Pereira de Medeiros
- RA: 1139603
- Nome completo: Camila Bueno
- RA: 1140231

> Antes da entrega, preencham os nomes completos e os RAs dos dois integrantes. Esses dados nao foram colocados para evitar inventar informacoes.

## Historia
Um jovem heroi, portador do Omnitrix, entra em uma selva tomada pelas criaturas de um vilao montado em um sapo gigante. Sem usar transformacoes, ele conta apenas com seus saltos e seus socos. O personagem fica fixo no eixo horizontal e se movimenta verticalmente por saltos com gravidade. Uma plataforma de pedra no meio da cena permite escapar dos ratinhos, mas e ali que os morcegos atacam na altura da cabeca. O jogador pode cair sobre os inimigos para elimina-los.

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
- W ou seta para cima: pular; e possivel aterrissar na plataforma.
- S ou seta para baixo: atravessar a plataforma durante o salto ou descer dela ate o chao.
- Pouse sobre ratinhos ou morcegos durante a descida para elimina-los e ganhar pontos.
- Z ou botao esquerdo do mouse: soco.
- SPACE: pausar/continuar.
- ESC: fechar o jogo.

## Funcionalidades
- Tela inicial tematizada (simbolo do Omnitrix animado, heroi em destaque, particulas de energia verde), com campo de nome, botao interativo e ranking Top 5.
- Tela de boas-vindas com nome do jogador, explicacao da mecanica e um unico botao para iniciar.
- A tela de boas-vindas mostra os melhores resultados com data e hora.
- O jogo tem tres vidas, mostradas por tres coracoes.
- O heroi ataca com um soco (Z ou clique).
- Ratinhos e morcegos surgem durante a partida e ficam mais rapidos e numerosos com o tempo.
- Os morcegos voam na altura da cabeca do heroi quando ele esta sobre a plataforma.
- O personagem permanece na mesma posicao horizontal e se movimenta verticalmente por saltos com aceleracao da gravidade, aterrissando na plataforma ou no chao.
- Pular sobre ratinhos ou morcegos elimina o inimigo, concede pontos e impulsiona o personagem para um novo salto.
- Um objeto decorativo se movimenta de forma aleatoria, sem interagir com o jogador.
- Um circulo amarelo no canto da tela pulsa lentamente.
- A tecla SPACE pausa o jogo e exibe PAUSE no centro.
- A mensagem ESPACO: PAUSAR aparece discretamente durante a partida.
- O jogo registra nome, pontuacao, data e hora no arquivo `log.dat` (formato HH:MM:SS).
- A tela de fim de jogo mostra o competidor com maior pontuacao.
- `pyttsx3` e utilizado na tela de boas-vindas.
- ESC fecha o jogo completamente.

## Alteracoes da V11
- Transformacoes removidas: sem menu do Omnitrix (G), sem Chamas, sem Bola de Canhao e sem animacao de transformacao. Os arquivos desses aliens foram retirados de `bases/`.
- Nova tela inicial desenhada no codigo, no tema do Omnitrix: simbolo animado, titulo com brilho verde, heroi animado em um pedestal de energia e controles atualizados.
- Morcegos nascem e voam na altura da cabeca do heroi sobre a plataforma, oscilando poucos pixels (antes eles iam descendo durante o voo).
- Plataforma encurtada para terminar antes do vilao e redesenhada com blocos de pedra, musgo, flores, cipos, pilares de pedra e simbolos do Omnitrix entalhados.

## Alteracoes da V10
- O movimento vertical agora usa impulso e gravidade: o heroi realiza saltos com arco natural, sem flutuar ate a plataforma.
- W/seta para cima inicia o salto; S/seta para baixo permite atravessar a plataforma durante o salto ou descer dela.
- Aterrissar sobre ratinhos ou morcegos elimina o inimigo, soma pontos e gera um impulso de ricochete.
- Foram adicionadas animacoes de pulo para o heroi.
- O botao de inicio foi corrigido para “COMEÇAR PARTIDA”.

## Audio
Os arquivos WAV desta versao foram compostos e sintetizados originalmente para o projeto: musica de fundo, soco, impacto, pontuacao, morte, pulo e interface. Todos ficam dentro de `bases/sons/`.

Consulte `bases/sons/FONTES_AUDIO.txt` para as referencias externas pesquisadas e informacoes de licenca.

## Estrutura principal
- `main.py`: codigo principal do jogo.
- `Recursos/trabalho.py`: funcoes auxiliares importadas pelo programa.
- `bases/imagens/`: cenario, personagem, inimigos, chefe e animacoes.
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
