import pygame
import random
import math
import os
from datetime import datetime
from Recursos.trabalho import criar_inimigo, mover_decoracao

# ------------------------------------------------------------
# CONFIGURACAO INICIAL
# ------------------------------------------------------------
pygame.init()

LARGURA = 1000
ALTURA = 700
CHAO = 535
# Plataforma elevada: o personagem pode subir ate sua superficie e descer
# novamente para o chao. Ela termina antes do vilao para nao cobri-lo.
PLATAFORMA_X = 55
PLATAFORMA_LARGURA = 560
PLATAFORMA_TOPO = 380
PLATAFORMA_ESPESSURA = 26
PILARES_X = (205, 400, 570)
# Altura (eixo y) da cabeca do heroi quando ele esta em pe sobre a plataforma.
# Os morcegos voam nessa faixa.
CABECA_NA_PLATAFORMA = PLATAFORMA_TOPO - 100
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Omnitrix Run - V11")

# Os caminhos usam a pasta deste arquivo. Assim o jogo abre mesmo
# quando o terminal foi iniciado em outra pasta.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
os.chdir(PASTA_PROJETO)
BASE = os.path.join(PASTA_PROJETO, "bases")

try:
    pygame.mixer.init()
except pygame.error:
    pass

clock = pygame.time.Clock()

PRETO = (8, 12, 10)
BRANCO = (245, 248, 245)
VERDE = (70, 220, 110)
VERDE_CLARO = (155, 255, 165)
VERDE_ESCURO = (20, 70, 40)
VERMELHO = (230, 75, 75)
AMARELO = (255, 220, 70)
CINZA_TEXTO = (185, 205, 190)

FONTE_PATH = os.path.join(BASE, "fontes", "DejaVuSans-Bold.ttf")


def fonte(tamanho):
    if os.path.exists(FONTE_PATH):
        return pygame.font.Font(FONTE_PATH, tamanho)
    return pygame.font.SysFont("Arial", tamanho, bold=True)


FONTE_CAPA = fonte(60)
FONTE_TITULO = fonte(54)
FONTE_GRANDE = fonte(40)
FONTE_MEDIA = fonte(27)
FONTE_PEQUENA = fonte(17)
FONTE_MENOR = fonte(14)
FONTE_ROTULO = fonte(12)
FONTE_MICRO = fonte(10)


def caminho_imagem(nome):
    return os.path.join(BASE, "imagens", nome)


def carregar_imagem(caminho):
    imagem = pygame.image.load(caminho).convert_alpha()
    return imagem


def carregar_animacao(nome, quantidade):
    imagens = []
    for numero in range(1, quantidade + 1):
        arquivo = nome + "_" + str(numero).zfill(2) + ".png"
        caminho = caminho_imagem(os.path.join("animacoes", nome, arquivo))
        imagens.append(carregar_imagem(caminho))
    return imagens


def carregar_som(nome):
    caminho = os.path.join(BASE, "sons", nome)
    if pygame.mixer.get_init() and os.path.exists(caminho):
        try:
            return pygame.mixer.Sound(caminho)
        except pygame.error:
            return None
    return None


def tocar_som(som):
    if som is not None:
        som.play()


# ------------------------------------------------------------
# IMAGENS E ANIMACOES
# ------------------------------------------------------------
FUNDO = pygame.transform.smoothscale(
    carregar_imagem(caminho_imagem("fundo.png")), (LARGURA, ALTURA)
)
OMNITRIX_IMG = carregar_imagem(caminho_imagem("icone_omnitrix.png"))
DECORACAO_IMG = carregar_imagem(caminho_imagem("decoracao.png"))

ANIMACAO_CAMINHAR = carregar_animacao("caminhar", 6)
ANIMACAO_ATACAR = carregar_animacao("atacar", 4)
ANIMACAO_PULAR = carregar_animacao("pular", 4)

# Heroi em tamanho maior, usado como destaque na tela inicial.
HEROI_CAPA_FRAMES = [
    pygame.transform.smoothscale(imagem, (214, 200)) for imagem in ANIMACAO_CAMINHAR
]

RATINHO_FRAMES = []
for numero in range(1, 7):
    arquivo = "ratinho_" + str(numero).zfill(2) + ".png"
    caminho = caminho_imagem(os.path.join("inimigos", "ratinho_corrida", arquivo))
    imagem = carregar_imagem(caminho)
    imagem = pygame.transform.smoothscale(imagem, (112, 72))
    # Os ratinhos da arte estao virados para a direita, mas correm para a esquerda.
    imagem = pygame.transform.flip(imagem, True, False)
    RATINHO_FRAMES.append(imagem)

# Morcego voador: seis quadros de uma animacao original para o jogo.
MORCEGO_FRAMES = []
for numero in range(1, 7):
    arquivo = "voar_" + str(numero).zfill(2) + ".png"
    caminho = caminho_imagem(os.path.join("inimigos", "morcego", arquivo))
    MORCEGO_FRAMES.append(carregar_imagem(caminho))

BOSS_IMG = carregar_imagem(caminho_imagem(os.path.join("chefes", "vilao_no_sapo.png")))
BOSS_IMG = pygame.transform.smoothscale(BOSS_IMG, (370, 270))

SOM_PONTO = carregar_som("ponto.wav")
SOM_MORTE = carregar_som("morte.wav")
SOM_SOCO = carregar_som("soco.wav")
SOM_IMPACTO = carregar_som("impacto.wav")
SOM_MENU = carregar_som("menu.wav")
SOM_PULO = carregar_som("pulo.wav")
MUSICA_FUNDO = os.path.join(BASE, "sons", "musica_fundo.wav")


def iniciar_musica():
    if pygame.mixer.get_init() and os.path.exists(MUSICA_FUNDO):
        try:
            pygame.mixer.music.load(MUSICA_FUNDO)
            pygame.mixer.music.set_volume(0.24)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass


def pausar_musica(pausada):
    if not pygame.mixer.get_init():
        return
    try:
        if pausada:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    except pygame.error:
        pass


# ------------------------------------------------------------
# FUNCOES DE TELA, PONTUACAO E VOZ
# ------------------------------------------------------------
def texto(conteudo, fonte_usada, cor, x, y, centro=False, superficie=None):
    if superficie is None:
        superficie = TELA
    imagem = fonte_usada.render(conteudo, True, cor)
    retangulo = imagem.get_rect()
    if centro:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    superficie.blit(imagem, retangulo)
    return retangulo


def texto_com_brilho(superficie, conteudo, fonte_usada, cor, cor_brilho, x, y, centro=False):
    """Escreve um texto com um contorno luminoso verde, como a luz do Omnitrix."""
    imagem = fonte_usada.render(conteudo, True, cor)
    brilho = fonte_usada.render(conteudo, True, cor_brilho)
    retangulo = imagem.get_rect()
    if centro:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    for distancia, transparencia in ((6, 35), (4, 60), (2, 110)):
        brilho.set_alpha(transparencia)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (1, 1), (-1, 1), (1, -1)):
            superficie.blit(brilho, (retangulo.x + dx * distancia,
                                     retangulo.y + dy * distancia))
    superficie.blit(imagem, retangulo)
    return retangulo


def painel(x, y, largura, altura, transparencia=190):
    camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
    camada.fill((5, 20, 12, transparencia))
    TELA.blit(camada, (x, y))
    pygame.draw.rect(TELA, VERDE, (x, y, largura, altura), 2, border_radius=14)


def painel_tecnologico(superficie, x, y, largura, altura, transparencia=215):
    """Painel com degrade, borda dupla e cantos de 'tecnologia alienigena'."""
    camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
    for linha in range(altura):
        t = linha / max(1, altura - 1)
        cor = (int(5 + 4 * t), int(30 - 14 * t), int(17 - 6 * t), transparencia)
        pygame.draw.line(camada, cor, (0, linha), (largura, linha))
    # Linhas horizontais bem discretas, como uma tela de monitor.
    for linha in range(0, altura, 4):
        pygame.draw.line(camada, (14, 44, 26, transparencia), (0, linha), (largura, linha))
    mascara = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, largura, altura),
                     border_radius=16)
    camada.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    superficie.blit(camada, (x, y))

    pygame.draw.rect(superficie, (46, 175, 88), (x, y, largura, altura), 2,
                     border_radius=16)
    pygame.draw.rect(superficie, VERDE_ESCURO, (x + 5, y + 5, largura - 10, altura - 10),
                     1, border_radius=12)
    tamanho = 18
    for canto_x, canto_y, sx, sy in ((x + 9, y + 9, 1, 1),
                                     (x + largura - 10, y + 9, -1, 1),
                                     (x + 9, y + altura - 10, 1, -1),
                                     (x + largura - 10, y + altura - 10, -1, -1)):
        pygame.draw.line(superficie, VERDE_CLARO, (canto_x, canto_y),
                         (canto_x + sx * tamanho, canto_y), 3)
        pygame.draw.line(superficie, VERDE_CLARO, (canto_x, canto_y),
                         (canto_x, canto_y + sy * tamanho), 3)


def ler_ranking(limite=5):
    melhores_jogadores = []
    caminho_log = os.path.join(PASTA_PROJETO, "log.dat")

    if os.path.exists(caminho_log):
        with open(caminho_log, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                partes = linha.strip().split("|")
                if len(partes) == 4:
                    try:
                        nome = partes[0].strip() or "Jogador"
                        pontos = int(partes[1])
                        registro = {
                            "nome": nome,
                            "pontos": pontos,
                            "data": partes[2],
                            "hora": partes[3]
                        }
                        encontrou = False
                        for jogador in melhores_jogadores:
                            if jogador["nome"].lower() == nome.lower():
                                encontrou = True
                                if pontos > jogador["pontos"]:
                                    jogador["pontos"] = pontos
                                    jogador["data"] = partes[2]
                                    jogador["hora"] = partes[3]
                                break
                        if not encontrou:
                            melhores_jogadores.append(registro)
                    except ValueError:
                        pass

    # Ordena do maior para o menor sem usar recursos avancados.
    for i in range(len(melhores_jogadores)):
        for j in range(i + 1, len(melhores_jogadores)):
            if melhores_jogadores[j]["pontos"] > melhores_jogadores[i]["pontos"]:
                temporario = melhores_jogadores[i]
                melhores_jogadores[i] = melhores_jogadores[j]
                melhores_jogadores[j] = temporario

    return melhores_jogadores[:limite]


def ler_recorde():
    ranking = ler_ranking(1)
    if ranking:
        recorde = ranking[0]
        return recorde["nome"], recorde["pontos"], recorde["data"], recorde["hora"]
    return "Ninguem", 0, "--/--/----", "--:--:--"


def salvar_log(nome, pontos):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    nome_log = nome.replace("|", " ").replace("\n", " ")
    with open(os.path.join(PASTA_PROJETO, "log.dat"), "a", encoding="utf-8") as arquivo:
        arquivo.write(nome_log + "|" + str(pontos) + "|" + data + "|" + hora + "\n")


def falar(mensagem):
    # A atividade solicita o uso de pyttsx3. Se a voz nao estiver instalada,
    # o restante do jogo continua normalmente.
    try:
        import pyttsx3
        voz = pyttsx3.init()
        voz.say(mensagem)
        voz.runAndWait()
        voz.stop()
    except Exception:
        pass


def desenhar_sol(tempo):
    raio = 25 + int(5 * math.sin(tempo * 0.002))
    pygame.draw.circle(TELA, AMARELO, (955, 45), raio)


def desenhar_omnitrix(superficie, centro_x, centro_y, raio, tempo):
    """Desenha o simbolo do Omnitrix (ampulheta verde) com brilho pulsante."""
    pulso = 0.5 + 0.5 * math.sin(tempo * 0.004)

    halo = pygame.Surface((raio * 4, raio * 4), pygame.SRCALPHA)
    for indice in range(6):
        raio_halo = int(raio * 1.05 + indice * raio * 0.12 + pulso * 6)
        pygame.draw.circle(halo, (70, 255, 125, max(0, 34 - indice * 5)),
                           (raio * 2, raio * 2), raio_halo)
    superficie.blit(halo, (centro_x - raio * 2, centro_y - raio * 2))

    # Aro metalico com marcacoes girando lentamente.
    pygame.draw.circle(superficie, (48, 54, 58), (centro_x, centro_y), raio)
    pygame.draw.circle(superficie, (128, 138, 142), (centro_x, centro_y), raio, 3)
    pygame.draw.circle(superficie, (24, 28, 30), (centro_x, centro_y), raio - 4, 2)
    for indice in range(8):
        angulo = tempo * 0.0008 + indice * (math.pi / 4)
        px = int(centro_x + math.cos(angulo) * (raio - 8))
        py = int(centro_y + math.sin(angulo) * (raio - 8))
        cor_luz = (110, 255, 145) if indice % 2 == 0 else (40, 120, 62)
        pygame.draw.circle(superficie, (20, 24, 26), (px, py), 4)
        pygame.draw.circle(superficie, cor_luz, (px, py), 2)

    # Face verde com a ampulheta preta recortada em circulo.
    face = int(raio * 0.66)
    pygame.draw.circle(superficie, (14, 18, 16), (centro_x, centro_y), face + 4)
    simbolo = pygame.Surface((face * 2, face * 2), pygame.SRCALPHA)
    cor_face = (60 + int(45 * pulso), 225 + int(30 * pulso), 95 + int(35 * pulso))
    simbolo.fill(cor_face)
    pygame.draw.polygon(simbolo, (12, 16, 14),
                        [(0, 0), (int(face * 0.80), face), (0, face * 2)])
    pygame.draw.polygon(simbolo, (12, 16, 14),
                        [(face * 2, 0), (int(face * 1.20), face), (face * 2, face * 2)])
    mascara = pygame.Surface((face * 2, face * 2), pygame.SRCALPHA)
    pygame.draw.circle(mascara, (255, 255, 255, 255), (face, face), face)
    simbolo.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    superficie.blit(simbolo, (centro_x - face, centro_y - face))
    # Reflexo de vidro na face.
    pygame.draw.arc(superficie, (220, 255, 225),
                    (centro_x - face + 5, centro_y - face + 5, face * 2 - 10, face * 2 - 10),
                    math.radians(100), math.radians(160), 2)


def desenhar_coracao(x, y, tamanho, cor, superficie=None):
    """Desenha um coracao simples para representar uma vida."""
    if superficie is None:
        superficie = TELA
    pontos = [
        (int(x + tamanho * 0.50), int(y + tamanho * 0.92)),
        (int(x + tamanho * 0.08), int(y + tamanho * 0.48)),
        (int(x + tamanho * 0.08), int(y + tamanho * 0.28)),
        (int(x + tamanho * 0.20), int(y + tamanho * 0.10)),
        (int(x + tamanho * 0.36), int(y + tamanho * 0.10)),
        (int(x + tamanho * 0.50), int(y + tamanho * 0.28)),
        (int(x + tamanho * 0.64), int(y + tamanho * 0.10)),
        (int(x + tamanho * 0.80), int(y + tamanho * 0.10)),
        (int(x + tamanho * 0.92), int(y + tamanho * 0.28)),
        (int(x + tamanho * 0.92), int(y + tamanho * 0.48))
    ]
    pygame.draw.polygon(superficie, cor, pontos)
    pygame.draw.lines(superficie, (255, 195, 195), True, pontos, 2)


def desenhar_vidas(vidas, x=820, y=27):
    for indice in range(3):
        cor = (238, 55, 66) if indice < vidas else (65, 78, 70)
        desenhar_coracao(x + indice * 48, y, 34, cor)


# ------------------------------------------------------------
# PLATAFORMA DE PEDRA COM MUSGO (desenhada uma unica vez)
# ------------------------------------------------------------
def variar_cor(cor, variacao, sorteio):
    ajuste = sorteio.randint(-variacao, variacao)
    return (max(0, min(255, cor[0] + ajuste)),
            max(0, min(255, cor[1] + ajuste)),
            max(0, min(255, cor[2] + ajuste)))


def desenhar_bloco_pedra(superficie, retangulo, cor_base, sorteio):
    """Bloco de pedra com luz, sombra, pintinhas e algumas rachaduras."""
    cor = variar_cor(cor_base, 10, sorteio)
    pygame.draw.rect(superficie, cor, retangulo, border_radius=3)
    clara = (min(255, cor[0] + 28), min(255, cor[1] + 28), min(255, cor[2] + 24))
    escura = (max(0, cor[0] - 24), max(0, cor[1] - 24), max(0, cor[2] - 22))
    pygame.draw.line(superficie, clara, (retangulo.left + 2, retangulo.top + 1),
                     (retangulo.right - 3, retangulo.top + 1), 2)
    pygame.draw.line(superficie, clara, (retangulo.left + 1, retangulo.top + 2),
                     (retangulo.left + 1, retangulo.bottom - 3), 1)
    pygame.draw.line(superficie, escura, (retangulo.left + 2, retangulo.bottom - 2),
                     (retangulo.right - 2, retangulo.bottom - 2), 2)
    pygame.draw.line(superficie, escura, (retangulo.right - 2, retangulo.top + 2),
                     (retangulo.right - 2, retangulo.bottom - 2), 1)
    for _ in range(max(2, retangulo.width * retangulo.height // 60)):
        px = sorteio.randint(retangulo.left + 3, max(retangulo.left + 3, retangulo.right - 4))
        py = sorteio.randint(retangulo.top + 3, max(retangulo.top + 3, retangulo.bottom - 4))
        superficie.set_at((px, py), escura if sorteio.random() < 0.6 else clara)
    if retangulo.width > 26 and sorteio.random() < 0.35:
        x_rachadura = sorteio.randint(retangulo.left + 8, retangulo.right - 8)
        pontos = [(x_rachadura, retangulo.top + 2)]
        for passo in range(1, 4):
            pontos.append((x_rachadura + sorteio.randint(-4, 4),
                           retangulo.top + 2 + passo * (retangulo.height - 4) // 3))
        pygame.draw.lines(superficie, escura, False, pontos, 1)


def desenhar_simbolo_entalhado(superficie, centro_x, centro_y, raio):
    """Simbolo do Omnitrix entalhado na pedra, com brilho verde suave."""
    brilho = pygame.Surface((raio * 4, raio * 4), pygame.SRCALPHA)
    pygame.draw.circle(brilho, (70, 255, 125, 45), (raio * 2, raio * 2), raio * 2)
    superficie.blit(brilho, (centro_x - raio * 2, centro_y - raio * 2))
    pygame.draw.circle(superficie, (25, 40, 28), (centro_x, centro_y), raio + 1)
    pygame.draw.circle(superficie, (90, 235, 125), (centro_x, centro_y), raio)
    pygame.draw.polygon(superficie, (25, 40, 28), [
        (centro_x - raio, centro_y - raio + 2), (centro_x - 1, centro_y),
        (centro_x - raio, centro_y + raio - 2)])
    pygame.draw.polygon(superficie, (25, 40, 28), [
        (centro_x + raio, centro_y - raio + 2), (centro_x + 1, centro_y),
        (centro_x + raio, centro_y + raio - 2)])


def criar_plataforma():
    """Gera a textura da plataforma: pilares, blocos de pedra, musgo e cipos."""
    sorteio = random.Random(11)
    margem_topo = 12
    altura = CHAO + 8 - (PLATAFORMA_TOPO - margem_topo)
    superficie = pygame.Surface((PLATAFORMA_LARGURA, altura), pygame.SRCALPHA)
    topo = margem_topo
    base_laje = topo + PLATAFORMA_ESPESSURA

    # Pilares de pedra empilhada, do chao ate a laje.
    for pilar_absoluto in PILARES_X:
        pilar_x = pilar_absoluto - PLATAFORMA_X
        largura_pilar = 30
        y = base_laje
        linha = 0
        while y < altura - 14:
            altura_bloco = min(17, altura - 14 - y)
            deslocamento = 2 if linha % 2 == 0 else -2
            bloco = pygame.Rect(pilar_x + deslocamento, y, largura_pilar, altura_bloco)
            desenhar_bloco_pedra(superficie, bloco, (74, 80, 70), sorteio)
            pygame.draw.rect(superficie, (28, 32, 28), bloco, 1, border_radius=3)
            y += altura_bloco
            linha += 1
        # Base mais larga apoiada no chao.
        pe = pygame.Rect(pilar_x - 7, altura - 16, largura_pilar + 14, 14)
        desenhar_bloco_pedra(superficie, pe, (66, 72, 62), sorteio)
        pygame.draw.rect(superficie, (28, 32, 28), pe, 1, border_radius=3)
        # Manchas de musgo subindo pelo pilar.
        for _ in range(7):
            mx = pilar_x + sorteio.randint(0, largura_pilar)
            my = sorteio.randint(base_laje + 4, altura - 18)
            pygame.draw.circle(superficie, (58, 120, 50), (mx, my), sorteio.randint(2, 4))

    # Sombra da laje projetada logo abaixo dela.
    sombra = pygame.Surface((PLATAFORMA_LARGURA - 16, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 80), sombra.get_rect())
    superficie.blit(sombra, (8, base_laje - 2))

    # Laje: duas fileiras de blocos de pedra intercalados.
    laje = pygame.Rect(0, topo, PLATAFORMA_LARGURA, PLATAFORMA_ESPESSURA)
    pygame.draw.rect(superficie, (30, 34, 30), laje, border_radius=8)
    altura_fileira = PLATAFORMA_ESPESSURA // 2
    for fileira in range(2):
        x = -sorteio.randint(0, 20) if fileira == 1 else 0
        y = topo + fileira * altura_fileira
        while x < PLATAFORMA_LARGURA:
            largura_bloco = sorteio.randint(34, 58)
            inicio = max(x, 0)
            fim = min(x + largura_bloco, PLATAFORMA_LARGURA)
            if fim - inicio > 6:
                bloco = pygame.Rect(inicio + 1, y + 1, fim - inicio - 2, altura_fileira - 1)
                desenhar_bloco_pedra(superficie, bloco, (88, 94, 84), sorteio)
            x += largura_bloco
    pygame.draw.rect(superficie, (24, 28, 24), laje, 2, border_radius=8)

    # Simbolos do Omnitrix entalhados na pedra.
    for simbolo_x in (PLATAFORMA_LARGURA // 2 - 90, PLATAFORMA_LARGURA // 2 + 90):
        desenhar_simbolo_entalhado(superficie, simbolo_x,
                                   topo + PLATAFORMA_ESPESSURA // 2 + 1, 6)

    # Camada de musgo no topo, com borda irregular escorrendo pela pedra.
    pontos_musgo = [(0, topo + 2)]
    for x in range(0, PLATAFORMA_LARGURA + 1, 5):
        profundidade = sorteio.randint(3, 8)
        if sorteio.random() < 0.12:
            profundidade += sorteio.randint(4, 9)
        pontos_musgo.append((x, topo + profundidade))
    pontos_musgo.append((PLATAFORMA_LARGURA, topo + 2))
    pontos_musgo.append((PLATAFORMA_LARGURA - 4, topo - 2))
    pontos_musgo.append((4, topo - 2))
    pygame.draw.polygon(superficie, (52, 118, 46), pontos_musgo)
    pygame.draw.line(superficie, (104, 178, 74), (4, topo - 1),
                     (PLATAFORMA_LARGURA - 5, topo - 1), 3)
    for x in range(3, PLATAFORMA_LARGURA - 3, 3):
        altura_folha = sorteio.randint(2, 8)
        inclinacao = sorteio.randint(-2, 2)
        cor_folha = (sorteio.randint(95, 150), sorteio.randint(175, 225), sorteio.randint(65, 95))
        pygame.draw.line(superficie, cor_folha, (x, topo),
                         (x + inclinacao, topo - altura_folha), 1)
    # Pequenas flores da selva sobre o musgo.
    for _ in range(9):
        fx = sorteio.randint(10, PLATAFORMA_LARGURA - 10)
        cor_flor = sorteio.choice([(255, 220, 90), (255, 140, 160), (180, 240, 255)])
        pygame.draw.circle(superficie, cor_flor, (fx, topo - 3), 2)

    # Cipos pendurados com folhas.
    for _ in range(9):
        cipo_x = sorteio.randint(14, PLATAFORMA_LARGURA - 14)
        comprimento = sorteio.randint(18, 62)
        fase = sorteio.random() * 6.28
        pontos = []
        for passo in range(0, comprimento + 1, 3):
            pontos.append((cipo_x + int(math.sin(fase + passo * 0.18) * 3),
                           base_laje - 2 + passo))
        if len(pontos) > 1:
            pygame.draw.lines(superficie, (40, 96, 38), False, pontos, 2)
        for indice in range(2, len(pontos), 3):
            fx, fy = pontos[indice]
            lado = 1 if indice % 2 == 0 else -1
            folha = pygame.Rect(0, 0, 8, 4)
            folha.center = (fx + lado * 4, fy)
            pygame.draw.ellipse(superficie, (86, 168, 62), folha)
        ponta_x, ponta_y = pontos[-1]
        pygame.draw.circle(superficie, (110, 190, 80), (ponta_x, ponta_y), 2)

    return superficie, (PLATAFORMA_X, PLATAFORMA_TOPO - margem_topo)


PLATAFORMA_IMG, PLATAFORMA_POSICAO = criar_plataforma()


def desenhar_plataforma():
    """Desenha a plataforma elevada que funciona como rota de desvio."""
    TELA.blit(PLATAFORMA_IMG, PLATAFORMA_POSICAO)


def desenhar_rodape():
    painel(12, 615, 976, 73, 165)
    texto("W/↑: pular   S/↓: atravessar a plataforma e descer",
          FONTE_MENOR, BRANCO, 28, 626)
    texto("Z ou clique: soco   Caia sobre os inimigos   SPACE: pausar   ESC: sair",
          FONTE_MENOR, VERDE_CLARO, 28, 653)
    texto("ESPACO: PAUSAR", FONTE_MENOR, BRANCO, 770, 590)


# ------------------------------------------------------------
# TELAS INICIAIS
# ------------------------------------------------------------
def criar_fundo_capa():
    """Cenario da selva escurecido com vinheta verde para a tela inicial."""
    fundo = FUNDO.copy()
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for linha in range(ALTURA):
        distancia = abs(linha - ALTURA * 0.45) / (ALTURA * 0.55)
        pygame.draw.line(camada, (2, 14, 8, int(120 + 95 * distancia)),
                         (0, linha), (LARGURA, linha))
    fundo.blit(camada, (0, 0))
    # Feixes de luz verde vindos do alto, como energia do Omnitrix.
    feixes = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for inicio_x, largura_feixe in ((250, 70), (520, 110), (760, 60)):
        pygame.draw.polygon(feixes, (90, 255, 140, 18), [
            (inicio_x, 0), (inicio_x + largura_feixe, 0),
            (inicio_x + largura_feixe + 220, ALTURA), (inicio_x + 220, ALTURA)])
    fundo.blit(feixes, (0, 0))
    return fundo


def criar_interface_capa():
    """Paineis e textos fixos da tela inicial (desenhados uma unica vez)."""
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # Cabecalho com titulo.
    painel_tecnologico(camada, 24, 16, 952, 114)
    titulo = texto_com_brilho(camada, "OMNITRIX", FONTE_CAPA, BRANCO, (70, 255, 125), 152, 26)
    texto_com_brilho(camada, "RUN", FONTE_CAPA, VERDE_CLARO, (70, 255, 125),
                     titulo.right + 18, 26)
    texto("SOBREVIVA À SELVA  •  DERROTE O VILÃO DO SAPO", FONTE_MENOR, CINZA_TEXTO,
          156, 100, superficie=camada)
    selo = pygame.Rect(836, 48, 112, 50)
    pygame.draw.rect(camada, (10, 52, 28), selo, border_radius=12)
    pygame.draw.rect(camada, VERDE, selo, 2, border_radius=12)
    texto("V11", FONTE_MEDIA, BRANCO, selo.centerx, selo.centery, True, camada)

    # Painel do heroi.
    painel_tecnologico(camada, 24, 142, 360, 480)
    texto("HERÓI DO OMNITRIX", FONTE_PEQUENA, VERDE_CLARO, 204, 172, True, camada)
    pygame.draw.line(camada, VERDE, (52, 192), (356, 192), 2)
    for indice in range(3):
        desenhar_coracao(84 + indice * 44, 508, 32, (238, 55, 66), camada)
    texto("3 VIDAS", FONTE_MEDIA, BRANCO, 228, 509, superficie=camada)
    texto("PULE SOBRE RATINHOS E MORCEGOS", FONTE_ROTULO, CINZA_TEXTO,
          204, 566, True, camada)
    texto("OU USE O SOCO PARA ELIMINÁ-LOS", FONTE_ROTULO, CINZA_TEXTO,
          204, 586, True, camada)

    # Painel de cadastro e ranking.
    painel_tecnologico(camada, 400, 142, 576, 480)
    texto("ENTRE NA SELVA", FONTE_MEDIA, BRANCO, 688, 176, True, camada)
    texto("DIGITE SEU NOME E PREPARE-SE PARA A MISSÃO", FONTE_ROTULO, CINZA_TEXTO,
          688, 204, True, camada)
    texto("ENTER PARA CONTINUAR", FONTE_MICRO, CINZA_TEXTO, 688, 356, True, camada)

    ranking = pygame.Rect(422, 372, 532, 234)
    pygame.draw.rect(camada, (6, 24, 14), ranking, border_radius=12)
    pygame.draw.rect(camada, (46, 175, 88), ranking, 2, border_radius=12)
    texto("TOP 5  •  MELHORES JOGADORES", FONTE_PEQUENA, VERDE_CLARO,
          688, 396, True, camada)
    pygame.draw.line(camada, VERDE, (442, 414), (934, 414), 2)
    texto("#", FONTE_MICRO, CINZA_TEXTO, 446, 421, superficie=camada)
    texto("JOGADOR", FONTE_MICRO, CINZA_TEXTO, 478, 421, superficie=camada)
    texto("PONTOS", FONTE_MICRO, CINZA_TEXTO, 706, 421, superficie=camada)
    texto("DATA / HORA", FONTE_MICRO, CINZA_TEXTO, 810, 421, superficie=camada)

    # Rodape com os controles atuais.
    painel_tecnologico(camada, 24, 634, 952, 52)
    texto("W/↑ PULAR   •   S/↓ DESCER   •   Z/CLIQUE SOCO   •   SPACE PAUSAR   •   ESC SAIR",
          FONTE_ROTULO, BRANCO, 500, 660, True, camada)
    return camada


def desenhar_particulas(tempo):
    """Particulas de energia verde subindo pela selva."""
    for indice in range(46):
        velocidade = 0.018 + (indice % 5) * 0.007
        x = (indice * 137 + int(math.sin(tempo * 0.0012 + indice) * 14)) % LARGURA
        y = ALTURA + 20 - ((tempo * velocidade + indice * 61) % (ALTURA + 40))
        raio = 1 + indice % 3
        intensidade = 0.5 + 0.5 * math.sin(tempo * 0.005 + indice)
        cor = (int(60 + 80 * intensidade), int(170 + 85 * intensidade), int(90 + 60 * intensidade))
        pygame.draw.circle(TELA, cor, (int(x), int(y)), raio)


def desenhar_heroi_capa(tempo):
    """Heroi animado sobre um pedestal com raios de energia do Omnitrix."""
    centro_x = 204
    base_y = 466
    raios = pygame.Surface((340, 300), pygame.SRCALPHA)
    centro_raios = (170, 150)
    for indice in range(12):
        angulo = tempo * 0.0004 + indice * (math.pi * 2 / 12)
        p1 = (centro_raios[0] + math.cos(angulo - 0.11) * 138,
              centro_raios[1] + math.sin(angulo - 0.11) * 138)
        p2 = (centro_raios[0] + math.cos(angulo + 0.11) * 138,
              centro_raios[1] + math.sin(angulo + 0.11) * 138)
        pygame.draw.polygon(raios, (80, 255, 130, 22), [centro_raios, p1, p2])
    pulso = 0.5 + 0.5 * math.sin(tempo * 0.004)
    pygame.draw.circle(raios, (70, 255, 125, int(28 + 25 * pulso)), centro_raios, 96)
    pygame.draw.circle(raios, (70, 255, 125, 40), centro_raios, 120, 2)
    pygame.draw.circle(raios, (70, 255, 125, 22), centro_raios, 138, 1)
    TELA.blit(raios, (centro_x - 170, base_y - 108 - 150))

    # Pedestal luminoso.
    pygame.draw.ellipse(TELA, (8, 40, 22), (centro_x - 92, base_y - 14, 184, 30))
    pygame.draw.ellipse(TELA, (70, 255, 125), (centro_x - 92, base_y - 14, 184, 30), 3)
    pygame.draw.ellipse(TELA, (40, 150, 76), (centro_x - 70, base_y - 8, 140, 18), 2)
    for indice in range(6):
        angulo = tempo * 0.002 + indice * (math.pi / 3)
        px = int(centro_x + math.cos(angulo) * 86)
        py = int(base_y + 1 + math.sin(angulo) * 13)
        pygame.draw.circle(TELA, (190, 255, 200), (px, py), 2)

    quadro = HEROI_CAPA_FRAMES[(tempo // 140) % len(HEROI_CAPA_FRAMES)]
    flutuar = int(math.sin(tempo * 0.003) * 3)
    TELA.blit(quadro, quadro.get_rect(midbottom=(centro_x, base_y + 6 + flutuar)))


def tela_nome():
    nome = ""
    digitando = True
    caixa_nome = pygame.Rect(430, 222, 516, 54)
    botao = pygame.Rect(430, 288, 516, 54)
    campo_ativo = True
    hover_anterior = False

    fundo_capa = criar_fundo_capa()
    interface_capa = criar_interface_capa()
    ranking = ler_ranking(5)

    while digitando:
        tempo = pygame.time.get_ticks()
        mouse = pygame.mouse.get_pos()
        sobre_botao = botao.collidepoint(mouse)
        if sobre_botao and not hover_anterior:
            tocar_som(SOM_MENU)
        hover_anterior = sobre_botao

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                if evento.key == pygame.K_RETURN and nome.strip() != "":
                    tocar_som(SOM_MENU)
                    digitando = False
                elif campo_ativo and evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif campo_ativo and len(nome) < 18 and evento.unicode.isprintable():
                    nome += evento.unicode
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if caixa_nome.collidepoint(evento.pos):
                    campo_ativo = True
                elif botao.collidepoint(evento.pos) and nome.strip() != "":
                    tocar_som(SOM_MENU)
                    digitando = False
                else:
                    campo_ativo = False

        TELA.blit(fundo_capa, (0, 0))
        desenhar_particulas(tempo)
        TELA.blit(interface_capa, (0, 0))
        desenhar_omnitrix(TELA, 88, 73, 42, tempo)
        desenhar_heroi_capa(tempo)

        # Campo do nome.
        pygame.draw.rect(TELA, (7, 30, 19), caixa_nome, border_radius=13)
        if campo_ativo:
            brilho_campo = int(60 + 60 * (0.5 + 0.5 * math.sin(tempo * 0.006)))
            pygame.draw.rect(TELA, (brilho_campo, 255, 150), caixa_nome, 2, border_radius=13)
        else:
            pygame.draw.rect(TELA, VERDE, caixa_nome, 2, border_radius=13)
        if nome.strip():
            texto_digitado = nome + ("|" if (tempo // 450) % 2 == 0 else "")
            texto(texto_digitado, FONTE_MEDIA, BRANCO, 450, caixa_nome.y + 11)
        else:
            texto("Clique aqui e digite seu nome", FONTE_PEQUENA,
                  (135, 170, 145), 450, caixa_nome.y + 16)

        # Botao com degrade e brilho passando quando o mouse esta em cima.
        brilho = int((math.sin(tempo * 0.005) + 1) * 10)
        fundo_botao = pygame.Surface(botao.size, pygame.SRCALPHA)
        for linha in range(botao.height):
            t = linha / botao.height
            cor_linha = (int(22 + brilho + 20 * (1 - t)), int(110 + brilho + 40 * (1 - t)),
                         int(52 + brilho + 20 * (1 - t)))
            if sobre_botao:
                cor_linha = (min(255, cor_linha[0] + 15), min(255, cor_linha[1] + 25),
                             min(255, cor_linha[2] + 15))
            pygame.draw.line(fundo_botao, cor_linha, (0, linha), (botao.width, linha))
        mascara_botao = pygame.Surface(botao.size, pygame.SRCALPHA)
        pygame.draw.rect(mascara_botao, (255, 255, 255, 255), mascara_botao.get_rect(),
                         border_radius=13)
        fundo_botao.blit(mascara_botao, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        TELA.blit(fundo_botao, botao.topleft)
        pygame.draw.rect(TELA, VERDE_CLARO if sobre_botao else VERDE,
                         botao, 3, border_radius=13)
        if sobre_botao:
            brilho_x = botao.left + 18 + int((tempo // 6) % (botao.width - 50))
            pygame.draw.line(TELA, (200, 255, 210), (brilho_x, botao.bottom - 8),
                             (brilho_x + 16, botao.top + 8), 3)
        cor_texto_botao = BRANCO if nome.strip() else (190, 220, 200)
        texto("CONTINUAR  ▶", FONTE_MEDIA, cor_texto_botao, botao.centerx, botao.centery, True)

        # Preenche o TOP 5 com os resultados reais de log.dat.
        for indice in range(5):
            y_linha = 440 + indice * 31
            linha = pygame.Rect(438, y_linha, 500, 27)
            pygame.draw.rect(TELA, (10, 34, 21), linha, border_radius=7)
            primeiro = indice == 0 and indice < len(ranking)
            pygame.draw.rect(TELA, AMARELO if primeiro else (35, 100, 54), linha, 1,
                             border_radius=7)
            if indice < len(ranking):
                registro = ranking[indice]
                nome_ranking = registro["nome"]
                if len(nome_ranking) > 17:
                    nome_ranking = nome_ranking[:16] + "…"
                cor_posicao = AMARELO if indice == 0 else VERDE_CLARO
                texto(str(indice + 1), FONTE_MENOR, cor_posicao, 448, y_linha + 5)
                texto(nome_ranking, FONTE_MENOR, BRANCO, 478, y_linha + 5)
                texto(str(registro["pontos"]), FONTE_MENOR, VERDE_CLARO, 706, y_linha + 5)
                data_hora = registro["data"] + " " + registro["hora"][:5]
                texto(data_hora, FONTE_ROTULO, CINZA_TEXTO, 810, y_linha + 7)
            else:
                texto(str(indice + 1), FONTE_MENOR, (100, 130, 110), 448, y_linha + 5)
                texto("—", FONTE_MENOR, (120, 145, 125), 478, y_linha + 5)
                texto("—", FONTE_MENOR, (120, 145, 125), 706, y_linha + 5)
                texto("—", FONTE_MENOR, (120, 145, 125), 810, y_linha + 5)

        if not ranking:
            texto("Jogue uma partida para aparecer no ranking.", FONTE_MICRO,
                  (150, 180, 155), 688, 596, True)

        pygame.display.flip()
        clock.tick(60)

    return nome.strip()


def tela_boas_vindas(nome):
    ranking = ler_ranking(5)
    botao = pygame.Rect(330, 555, 340, 62)
    hover_anterior = False

    while True:
        sobre_botao = botao.collidepoint(pygame.mouse.get_pos())
        if sobre_botao and not hover_anterior:
            tocar_som(SOM_MENU)
        hover_anterior = sobre_botao

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao.collidepoint(evento.pos):
                    tocar_som(SOM_MENU)
                    falar("Prepare-se para a aventura na selva.")
                    return

        TELA.blit(FUNDO, (0, 0))
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((2, 10, 7, 115))
        TELA.blit(camada, (0, 0))

        painel(42, 28, 916, 644, 225)
        pygame.draw.rect(TELA, VERDE_CLARO, (65, 48, 870, 5), border_radius=3)
        desenhar_omnitrix(TELA, 500, 84, 26, pygame.time.get_ticks())
        texto("OMNITRIX RUN", FONTE_TITULO, VERDE_CLARO, 500, 145, True)
        texto("SOBREVIVA A SELVA. DERROTE O VILAO.", FONTE_PEQUENA, BRANCO, 500, 188, True)

        # Cartao esquerdo: boas-vindas, historia e controles.
        painel(72, 205, 410, 325, 205)
        texto("BEM-VINDO,", FONTE_MEDIA, VERDE_CLARO, 102, 230)
        texto(nome[:18], FONTE_GRANDE, BRANCO, 102, 267)
        texto("Sua missao", FONTE_PEQUENA, AMARELO, 102, 326)
        texto("Enfrente as criaturas enviadas pelo vilao", FONTE_MENOR, BRANCO, 102, 352)
        texto("montado no sapo e sobreviva na selva.", FONTE_MENOR, BRANCO, 102, 374)
        texto("COMO JOGAR", FONTE_PEQUENA, VERDE_CLARO, 102, 414)
        texto("• W/↑: pule para subir na plataforma.", FONTE_MENOR, BRANCO, 102, 440)
        texto("• S/↓: desca ou atravesse a plataforma no ar.", FONTE_MENOR, BRANCO, 102, 462)
        texto("• Caia em cima dos inimigos ou use o soco (Z).", FONTE_MENOR, BRANCO, 102, 484)
        texto("• Voce tem 3 vidas: desvie dos morcegos!", FONTE_MENOR, BRANCO, 102, 506)

        # Cartao direito: ranking dos cinco melhores jogadores.
        painel(502, 205, 426, 325, 205)
        texto("TOP 5 JOGADORES", FONTE_MEDIA, VERDE_CLARO, 715, 238, True)
        texto("MELHORES PONTUACOES", FONTE_MENOR, BRANCO, 715, 264, True)
        pygame.draw.line(TELA, VERDE, (525, 286), (905, 286), 2)

        if ranking:
            for indice in range(5):
                y_linha = 297 + indice * 43
                pygame.draw.rect(TELA, (14, 36, 24), (520, y_linha, 390, 39), border_radius=7)
                if indice < len(ranking):
                    registro = ranking[indice]
                    cor_posicao = AMARELO if indice == 0 else VERDE_CLARO
                    nome_ranking = registro["nome"]
                    if len(nome_ranking) > 15:
                        nome_ranking = nome_ranking[:14] + "…"
                    texto(str(indice + 1), FONTE_PEQUENA, cor_posicao, 533, y_linha + 3)
                    texto(nome_ranking, FONTE_MENOR, BRANCO, 565, y_linha + 3)
                    texto(str(registro["pontos"]) + " pts", FONTE_MENOR, VERDE_CLARO, 795, y_linha + 3)
                    texto(registro["data"] + "  " + registro["hora"], FONTE_MENOR, (190, 210, 195), 565, y_linha + 21)
                else:
                    texto(str(indice + 1), FONTE_PEQUENA, (115, 145, 125), 533, y_linha + 3)
                    texto("--", FONTE_MENOR, (145, 165, 150), 565, y_linha + 3)
        else:
            texto("Ainda nao ha partidas registradas.", FONTE_PEQUENA, BRANCO, 715, 360, True)
            texto("Seja o primeiro a entrar no ranking!", FONTE_MENOR, VERDE_CLARO, 715, 389, True)

        # Unico botao da tela, como pede a atividade.
        brilho_botao = int((math.sin(pygame.time.get_ticks() * 0.005) + 1) * 8)
        cor_inicio = (18 + brilho_botao, 85 + brilho_botao, 42 + brilho_botao)
        if sobre_botao:
            cor_inicio = (28, 125, 62)
        pygame.draw.rect(TELA, cor_inicio, botao, border_radius=15)
        pygame.draw.rect(TELA, VERDE_CLARO if sobre_botao else VERDE,
                         botao, 3, border_radius=15)
        texto("COMEÇAR PARTIDA", FONTE_MEDIA, BRANCO, botao.centerx, botao.centery, True)
        texto("W/↑ pular | S/↓ atravessar a plataforma e descer",
              FONTE_MENOR, BRANCO, 500, 632, True)
        texto("Z/Clique soco | ESPACO pausa | ESC sair",
              FONTE_MENOR, (190, 210, 195), 500, 654, True)

        pygame.display.flip()
        clock.tick(60)


# ------------------------------------------------------------
# PARTIDA
# ------------------------------------------------------------
def jogar(nome):
    jogador_x = 105
    jogador_y = float(CHAO)
    velocidade_pulo = 0.0
    esta_no_ar = False
    ignorar_plataforma = False
    olhando_esquerda = False

    pontos = 0
    inimigos = []
    morcegos = []
    tempo_inimigo = 0
    tempo_morcego = 0
    tempo_partida = 0
    vidas = 3

    pausa = False
    acabou = False

    ataque_ativo = False
    tempo_ataque = 0
    frame_ataque = 0
    soco_acertou = False

    invulneravel = 0

    decor_x = 680
    decor_y = 175
    decor_vx = random.choice([-2, -1, 1, 2])
    decor_vy = random.choice([-1, 1])

    while not acabou:
        dt = clock.tick(60)
        tempo = pygame.time.get_ticks()

        # EVENTOS DO TECLADO E MOUSE
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

                if evento.key == pygame.K_SPACE:
                    pausa = not pausa
                    pausar_musica(pausa)

                elif not pausa:
                    if (evento.key in (pygame.K_w, pygame.K_UP)
                            and not esta_no_ar and not ataque_ativo):
                        # Impulso inicial + gravidade formam um arco de salto real.
                        velocidade_pulo = -850.0
                        esta_no_ar = True
                        ignorar_plataforma = False
                        tocar_som(SOM_PULO)
                    elif (evento.key in (pygame.K_s, pygame.K_DOWN)
                            and esta_no_ar and jogador_y <= PLATAFORMA_TOPO):
                        # Durante um salto, permite atravessar a plataforma na descida.
                        ignorar_plataforma = True
                    elif (evento.key in (pygame.K_s, pygame.K_DOWN)
                            and not esta_no_ar and abs(jogador_y - PLATAFORMA_TOPO) < 2):
                        # Da plataforma, o personagem pode descer ate o chao.
                        esta_no_ar = True
                        ignorar_plataforma = True
                        velocidade_pulo = 180.0
                    elif evento.key == pygame.K_z and not ataque_ativo:
                        ataque_ativo = True
                        tempo_ataque = 0
                        frame_ataque = 0
                        soco_acertou = False
                        tocar_som(SOM_SOCO)

            if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                    and not pausa and not ataque_ativo):
                ataque_ativo = True
                tempo_ataque = 0
                frame_ataque = 0
                soco_acertou = False
                tocar_som(SOM_SOCO)

        # TAMANHO DA AREA DE COLISAO DO PERSONAGEM
        jogador_largura = 74
        jogador_altura = 116

        # ATUALIZACAO DO JOGO
        if not pausa:
            tempo_partida += dt
            y_antes_do_movimento = jogador_y

            if esta_no_ar:
                # A gravidade continua atuando mesmo durante o soco.
                dt_segundos = min(dt / 1000.0, 0.05)
                velocidade_pulo += 1900.0 * dt_segundos
                jogador_y += velocidade_pulo * dt_segundos

                # Aterrissagem na plataforma: so acontece durante a descida.
                jogador_tem_acesso_plataforma = (
                    jogador_x + 74 > PLATAFORMA_X
                    and jogador_x < PLATAFORMA_X + PLATAFORMA_LARGURA
                )
                if (velocidade_pulo > 0 and not ignorar_plataforma
                        and jogador_tem_acesso_plataforma
                        and y_antes_do_movimento <= PLATAFORMA_TOPO
                        and jogador_y >= PLATAFORMA_TOPO):
                    jogador_y = float(PLATAFORMA_TOPO)
                    velocidade_pulo = 0.0
                    esta_no_ar = False
                elif jogador_y >= CHAO:
                    jogador_y = float(CHAO)
                    velocidade_pulo = 0.0
                    esta_no_ar = False
                    ignorar_plataforma = False

            jogador = pygame.Rect(
                int(jogador_x), int(jogador_y) - jogador_altura,
                jogador_largura, jogador_altura
            )

            # ANIMACAO DO SOCO
            if ataque_ativo:
                tempo_ataque += dt
                if tempo_ataque >= 95:
                    frame_ataque += 1
                    tempo_ataque = 0
                    if frame_ataque >= len(ANIMACAO_ATACAR):
                        ataque_ativo = False
                        frame_ataque = 0

                if not soco_acertou and frame_ataque >= 2:
                    if olhando_esquerda:
                        area_soco = pygame.Rect(jogador.left - 55, jogador.top + 15, 65, jogador.height - 20)
                    else:
                        area_soco = pygame.Rect(jogador.right - 5, jogador.top + 15, 65, jogador.height - 20)
                    for inimigo in inimigos[:]:
                        rat_rect = pygame.Rect(int(inimigo[0]) + 8, int(inimigo[1]) + 10, 94, 52)
                        if area_soco.colliderect(rat_rect):
                            inimigos.remove(inimigo)
                            pontos += 10
                            soco_acertou = True
                            tocar_som(SOM_IMPACTO)
                            tocar_som(SOM_PONTO)
                            break
                    if not soco_acertou:
                        for morcego in morcegos[:]:
                            bat_rect = pygame.Rect(int(morcego[0]) + 20, int(morcego[1]) + 20, 76, 54)
                            if area_soco.colliderect(bat_rect):
                                morcegos.remove(morcego)
                                pontos += 15
                                soco_acertou = True
                                tocar_som(SOM_IMPACTO)
                                tocar_som(SOM_PONTO)
                                break

            if invulneravel > 0:
                invulneravel -= dt

            decor_x, decor_y, decor_vx, decor_vy = mover_decoracao(
                decor_x, decor_y, decor_vx, decor_vy, LARGURA, ALTURA
            )

            # OS RATINHOS COMECAM COM ESPACO ENTRE AS ONDAS E ACELERAM MAIS CEDO.
            # O intervalo entre ondas diminui e os grupos ficam maiores ao longo da partida.
            tempo_inimigo += dt
            velocidade_ratinhos = min(9.5, 2.8 + tempo_partida * 0.000085)
            intervalo_ratinhos = max(650, 2050 - tempo_partida * 0.0095)

            if tempo_inimigo >= intervalo_ratinhos:
                y_inimigo = CHAO - 68
                quantidade_ratinhos = 1
                if tempo_partida >= 25000:
                    quantidade_ratinhos = 2
                if tempo_partida >= 60000:
                    quantidade_ratinhos = 3
                for indice in range(quantidade_ratinhos):
                    novo_inimigo = criar_inimigo(LARGURA + indice * 155, y_inimigo, velocidade_ratinhos)
                    novo_inimigo.append(0)  # frame da corrida
                    novo_inimigo.append(0)  # tempo do frame
                    inimigos.append(novo_inimigo)
                tempo_inimigo = 0

            # Morcegos voam na altura da cabeca do heroi quando ele esta sobre a
            # plataforma; o salto e a queda permitem desviar ou elimina-los por cima.
            tempo_morcego += dt
            velocidade_morcegos = min(8.5, 2.8 + tempo_partida * 0.000065)
            intervalo_morcegos = max(1000, 5000 - tempo_partida * 0.025)
            if tempo_morcego >= intervalo_morcegos:
                quantidade_morcegos = 1
                if tempo_partida >= 30000:
                    quantidade_morcegos = 2
                if tempo_partida >= 75000:
                    quantidade_morcegos = 3
                for indice in range(quantidade_morcegos):
                    x_morcego = random.randint(570, 930) + indice * 35
                    # O centro da area de colisao fica 47 px abaixo do topo da imagem.
                    y_morcego = CABECA_NA_PLATAFORMA - 47 + random.randint(-6, 6)
                    fase = random.uniform(0, math.pi * 2)
                    # [x, y, quadro, tempo do quadro, altura base, fase do voo]
                    morcegos.append([float(x_morcego), float(y_morcego), 0, 0,
                                     float(y_morcego), fase])
                tempo_morcego = 0

            # MOVIMENTO E ANIMACAO DOS RATINHOS
            for inimigo in inimigos[:]:
                # Todos os ratinhos vivos acompanham a dificuldade atual.
                inimigo[2] = velocidade_ratinhos
                inimigo[0] -= inimigo[2]
                inimigo[4] += dt
                if inimigo[4] >= 105:
                    inimigo[3] = (inimigo[3] + 1) % len(RATINHO_FRAMES)
                    inimigo[4] = 0

                if inimigo[0] < -125:
                    inimigos.remove(inimigo)
                    continue

                rat_rect = pygame.Rect(int(inimigo[0]) + 8, int(inimigo[1]) + 10, 94, 52)

                # Se o jogador estiver caindo e cruzar a parte de cima do ratinho,
                # ele elimina o inimigo e ganha um pequeno impulso para outro salto.
                pisou_no_ratinho = (
                    esta_no_ar and velocidade_pulo > 0
                    and y_antes_do_movimento <= rat_rect.top + 8
                    and jogador.bottom >= rat_rect.top
                    and jogador.right > rat_rect.left
                    and jogador.left < rat_rect.right
                )
                if pisou_no_ratinho:
                    inimigos.remove(inimigo)
                    jogador_y = float(rat_rect.top)
                    jogador.bottom = rat_rect.top
                    velocidade_pulo = -470.0
                    pontos += 25
                    invulneravel = max(invulneravel, 250)
                    tocar_som(SOM_IMPACTO)
                    tocar_som(SOM_PONTO)
                    continue

                # Contato lateral tira uma vida; durante a subida do salto o inimigo
                # pode ser ultrapassado sem causar dano.
                area_jogador = pygame.Rect(
                    jogador.left + 8, jogador.top + 16,
                    max(1, jogador.width - 16), max(1, jogador.height - 24)
                )
                area_ratinho = pygame.Rect(int(inimigo[0]) + 12, int(inimigo[1]) + 8, 88, 60)
                if (area_jogador.colliderect(area_ratinho)
                        and invulneravel <= 0
                        and not (esta_no_ar and velocidade_pulo < 0)):
                    if inimigo in inimigos:
                        inimigos.remove(inimigo)
                    vidas -= 1
                    invulneravel = 1300
                    tocar_som(SOM_IMPACTO)
                    if vidas <= 0:
                        tocar_som(SOM_MORTE)
                        acabou = True
                    continue

            # MOVIMENTO, ANIMACAO E COLISAO DOS MORCEGOS
            for morcego in morcegos[:]:
                morcego[0] -= velocidade_morcegos
                # Oscila poucos pixels em torno da altura base, sem descer aos poucos.
                morcego[1] = morcego[4] + math.sin(tempo * 0.006 + morcego[5]) * 6

                morcego[3] += dt
                if morcego[3] >= 105:
                    morcego[2] = (morcego[2] + 1) % len(MORCEGO_FRAMES)
                    morcego[3] = 0

                bat_rect = pygame.Rect(int(morcego[0]) + 20, int(morcego[1]) + 20, 76, 54)

                # Tambem e possivel eliminar morcegos pousando sobre eles durante a descida.
                pisou_no_morcego = (
                    esta_no_ar and velocidade_pulo > 0
                    and y_antes_do_movimento <= bat_rect.top + 8
                    and jogador.bottom >= bat_rect.top
                    and jogador.right > bat_rect.left
                    and jogador.left < bat_rect.right
                )
                if pisou_no_morcego:
                    morcegos.remove(morcego)
                    jogador_y = float(bat_rect.top)
                    jogador.bottom = bat_rect.top
                    velocidade_pulo = -470.0
                    pontos += 30
                    invulneravel = max(invulneravel, 250)
                    tocar_som(SOM_IMPACTO)
                    tocar_som(SOM_PONTO)
                    continue

                # O contato lateral tira uma vida; durante a subida do salto o morcego
                # pode ser ultrapassado sem causar dano.
                if (jogador.colliderect(bat_rect)
                        and not (esta_no_ar and velocidade_pulo < 0)):
                    if morcego in morcegos:
                        morcegos.remove(morcego)
                    if invulneravel <= 0:
                        vidas -= 1
                        invulneravel = 1300
                        tocar_som(SOM_IMPACTO)
                        if vidas <= 0:
                            tocar_som(SOM_MORTE)
                            acabou = True
                    continue

                if morcego[0] < -130:
                    if morcego in morcegos:
                        morcegos.remove(morcego)
        else:
            jogador = pygame.Rect(
                int(jogador_x), int(jogador_y) - jogador_altura,
                jogador_largura, jogador_altura
            )

        # ----------------------------------------------------
        # DESENHO DA CENA
        # ----------------------------------------------------
        TELA.blit(FUNDO, (0, 0))
        desenhar_sol(tempo)
        TELA.blit(DECORACAO_IMG, (int(decor_x), int(decor_y)))

        # A plataforma termina antes do vilao, que fica sempre totalmente visivel.
        desenhar_plataforma()
        boss_rect = BOSS_IMG.get_rect(midbottom=(830, CHAO + 4))
        TELA.blit(BOSS_IMG, boss_rect)

        for inimigo in inimigos:
            imagem_rat = RATINHO_FRAMES[inimigo[3]]
            TELA.blit(imagem_rat, (int(inimigo[0]), int(inimigo[1])))

        for morcego in morcegos:
            imagem_morcego = MORCEGO_FRAMES[morcego[2]]
            TELA.blit(imagem_morcego, (int(morcego[0]), int(morcego[1])))

        # Escolha do quadro do heroi: soco, salto ou parado.
        if ataque_ativo:
            imagem_jogador = ANIMACAO_ATACAR[min(frame_ataque, len(ANIMACAO_ATACAR) - 1)]
        elif esta_no_ar:
            imagem_jogador = ANIMACAO_PULAR[(tempo // 105) % len(ANIMACAO_PULAR)]
        else:
            imagem_jogador = ANIMACAO_CAMINHAR[0]
        imagem_jogador = pygame.transform.smoothscale(imagem_jogador, (132, 124))

        if olhando_esquerda:
            imagem_jogador = pygame.transform.flip(imagem_jogador, True, False)

        posicao_jogador = imagem_jogador.get_rect(
            midbottom=(int(jogador.centerx), int(jogador.bottom))
        )
        # Pisca por um instante depois de sofrer dano, indicando invulnerabilidade.
        mostrar_jogador = not (invulneravel > 0 and (tempo // 100) % 2 == 0)
        if mostrar_jogador:
            TELA.blit(imagem_jogador, posicao_jogador)

        # Interface: pontuacao e tres coracoes para mostrar as vidas.
        painel(12, 12, 355, 58, 190)
        icone_hud = pygame.transform.smoothscale(OMNITRIX_IMG, (46, 46))
        TELA.blit(icone_hud, (20, 18))
        texto("Pontos: " + str(pontos), FONTE_MEDIA, BRANCO, 78, 26)
        painel(810, 12, 178, 58, 190)
        texto("VIDAS", FONTE_MENOR, BRANCO, 822, 14)
        desenhar_vidas(vidas, 820, 31)
        desenhar_rodape()

        if pausa:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((0, 0, 0, 180))
            TELA.blit(camada, (0, 0))
            texto("PAUSE", FONTE_TITULO, VERDE_CLARO, LARGURA//2, ALTURA//2, True)
            texto("Pressione ESPACO para continuar", FONTE_PEQUENA, BRANCO,
                  LARGURA//2, ALTURA//2 + 65, True)

        pygame.display.flip()

    salvar_log(nome, pontos)
    return pontos


def tela_morte(nome, pontos):
    recorde_nome, recorde_pontos, recorde_data, recorde_hora = ler_recorde()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                if evento.key == pygame.K_RETURN:
                    return

        TELA.blit(FUNDO, (0, 0))
        painel(170, 80, 660, 520, 220)
        texto("FIM DE JOGO", FONTE_TITULO, VERMELHO, 500, 160, True)
        texto(nome + " fez " + str(pontos) + " pontos.", FONTE_MEDIA, BRANCO, 500, 255, True)
        texto("Maior competidor:", FONTE_MEDIA, VERDE_CLARO, 500, 355, True)
        texto(recorde_nome + " - " + str(recorde_pontos) + " pontos",
              FONTE_GRANDE, BRANCO, 500, 410, True)
        texto("Data: " + recorde_data + "  Hora: " + recorde_hora,
              FONTE_PEQUENA, BRANCO, 500, 465, True)
        texto("ENTER para jogar novamente", FONTE_PEQUENA, VERDE_CLARO, 500, 535, True)
        texto("ESC para fechar", FONTE_PEQUENA, BRANCO, 500, 568, True)
        pygame.display.flip()
        clock.tick(60)


def main():
    iniciar_musica()
    while True:
        nome = tela_nome()
        tela_boas_vindas(nome)
        pontos = jogar(nome)
        tela_morte(nome, pontos)


if __name__ == "__main__":
    main()
    pygame.quit()
