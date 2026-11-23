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
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Omnitrix Run - V8 Animacoes Unificadas")

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
VERMELHO = (230, 75, 75)
AMARELO = (255, 220, 70)

COOLDOWN_CHAMAS = 1500
COOLDOWN_BOLA = 1500
ALTURA_PULO = 145

FONTE_PATH = os.path.join(BASE, "fontes", "DejaVuSans-Bold.ttf")


def fonte(tamanho):
    if os.path.exists(FONTE_PATH):
        return pygame.font.Font(FONTE_PATH, tamanho)
    return pygame.font.SysFont("Arial", tamanho, bold=True)


FONTE_TITULO = fonte(54)
FONTE_GRANDE = fonte(40)
FONTE_MEDIA = fonte(27)
FONTE_PEQUENA = fonte(17)
FONTE_MENOR = fonte(14)
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


def ajustar_sprite(imagem, largura, altura):
    """Redimensiona sem deformar e alinha o personagem pelos pes."""
    largura_original, altura_original = imagem.get_size()
    escala = min(largura / largura_original, altura / altura_original)
    nova_largura = max(1, int(largura_original * escala))
    nova_altura = max(1, int(altura_original * escala))
    imagem_redimensionada = pygame.transform.smoothscale(
        imagem, (nova_largura, nova_altura)
    )
    quadro = pygame.Surface((largura, altura), pygame.SRCALPHA)
    quadro.blit(imagem_redimensionada,
                ((largura - nova_largura) // 2, altura - nova_altura))
    return quadro


def ajustar_sprite_altura_visivel(imagem, largura, altura, altura_personagem):
    """Padroniza a altura do desenho visivel, ignorando margens transparentes."""
    limites = imagem.get_bounding_rect()
    if limites.width > 0 and limites.height > 0:
        imagem = imagem.subsurface(limites).copy()
    proporcao = min(altura_personagem / imagem.get_height(),
                    (largura - 8) / imagem.get_width())
    nova_largura = max(1, int(imagem.get_width() * proporcao))
    nova_altura = max(1, int(imagem.get_height() * proporcao))
    imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))
    quadro = pygame.Surface((largura, altura), pygame.SRCALPHA)
    quadro.blit(imagem, ((largura - nova_largura) // 2, altura - nova_altura - 2))
    return quadro


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
CAPA_IMG = pygame.transform.smoothscale(
    carregar_imagem(caminho_imagem("capa.png")), (LARGURA, ALTURA)
)
OMNITRIX_IMG = carregar_imagem(caminho_imagem("icone_omnitrix.png"))
DECORACAO_IMG = carregar_imagem(caminho_imagem("decoracao.png"))

ANIMACAO_CAMINHAR = carregar_animacao("caminhar", 6)
ANIMACAO_CORRER = carregar_animacao("correr", 6)
ANIMACAO_ATACAR = carregar_animacao("atacar", 4)
ANIMACAO_PULAR = carregar_animacao("pular", 4)
ANIMACAO_ROLAR = carregar_animacao("rolar", 6)
ANIMACAO_MORRER = carregar_animacao("morrer", 6)
ANIMACAO_TRANSFORMAR = carregar_animacao("transformar", 8)
ANIMACAO_AGACHAR = carregar_animacao("agachar", 4)

ALIEN_CHAMAS_IMG = carregar_imagem(caminho_imagem(os.path.join("aliens", "chamas.png")))
ALIEN_BOLA_IMG = carregar_imagem(caminho_imagem(os.path.join("aliens", "bola_de_canhao.png")))

# Chamas: todos os quadros agora usam a mesma altura visivel e o mesmo canvas.
CHAMAS_PARADO_FRAMES = []
for numero in range(1, 5):
    arquivo = "chamas_parado_" + str(numero).zfill(2) + ".png"
    caminho = caminho_imagem(os.path.join("animacoes", "chamas_parado", arquivo))
    CHAMAS_PARADO_FRAMES.append(
        carregar_imagem(caminho)
    )

CHAMAS_CORRER_FRAMES = []
for numero in range(1, 7):
    arquivo = "chamas_" + str(numero).zfill(2) + ".png"
    caminho = caminho_imagem(os.path.join("animacoes", "chamas_correndo", arquivo))
    CHAMAS_CORRER_FRAMES.append(
        carregar_imagem(caminho)
    )

# Bola de Canhao: todas as animacoes usam o mesmo modelo pixel-art preferido.
# O conjunto antigo de repouso e o modelo antigo de rolamento nao sao mais usados.
BOLA_PARADO_FRAMES = carregar_animacao("bola_parado", 4)
BOLA_CAMINHAR_FRAMES = carregar_animacao("bola_caminhar", 6)
BOLA_CORRER_FRAMES = carregar_animacao("bola_correr", 6)
BOLA_PULAR_FRAMES = carregar_animacao("bola_pular", 4)
BOLA_AGACHAR_FRAMES = carregar_animacao("bola_agachar", 4)
BOLA_ATACAR_FRAMES = carregar_animacao("bola_atacar", 6)

# Todos os quadros da Bola usam o mesmo tamanho para nao mudar a escala na tela.
BOLA_PARADO_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_PARADO_FRAMES]
BOLA_CAMINHAR_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_CAMINHAR_FRAMES]
BOLA_CORRER_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_CORRER_FRAMES]
BOLA_PULAR_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_PULAR_FRAMES]
BOLA_AGACHAR_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_AGACHAR_FRAMES]
BOLA_ATACAR_FRAMES = [ajustar_sprite(imagem, 154, 150) for imagem in BOLA_ATACAR_FRAMES]

BOLA_FOGO_BASE = carregar_imagem(caminho_imagem(os.path.join("efeitos", "bola_de_fogo.png")))
BOLA_FOGO_IMG = pygame.transform.rotate(
    pygame.transform.smoothscale(BOLA_FOGO_BASE, (52, 82)), -55
)
BOLA_FOGO_ESQUERDA_IMG = pygame.transform.flip(BOLA_FOGO_IMG, True, False)

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
SOM_TIRO = carregar_som("tiro.wav")
SOM_IMPACTO = carregar_som("impacto.wav")
SOM_TRANSFORMACAO = carregar_som("transformacao.wav")
SOM_MENU = carregar_som("menu.wav")
SOM_PULO = carregar_som("pulo.wav")
SOM_ROLAGEM = carregar_som("rolagem.wav")
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


def criar_bola_fogo(jogador_x, olhando_esquerda, deslocamento_pulo):
    """Cria um projetil do Chamas voltado para o lado em que o jogador olha."""
    imagem_fogo = BOLA_FOGO_ESQUERDA_IMG if olhando_esquerda else BOLA_FOGO_IMG
    fogo_rect = imagem_fogo.get_rect()
    fogo_rect.centery = CHAO - 75 - deslocamento_pulo
    if olhando_esquerda:
        fogo_rect.midright = (int(jogador_x), fogo_rect.centery)
        velocidade_fogo = -12
    else:
        fogo_rect.midleft = (int(jogador_x + 80), fogo_rect.centery)
        velocidade_fogo = 12
    return [fogo_rect, velocidade_fogo]


# ------------------------------------------------------------
# FUNCOES DE TELA, PONTUACAO E VOZ
# ------------------------------------------------------------
def texto(conteudo, fonte_usada, cor, x, y, centro=False):
    imagem = fonte_usada.render(conteudo, True, cor)
    retangulo = imagem.get_rect()
    if centro:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    TELA.blit(imagem, retangulo)


def painel(x, y, largura, altura, transparencia=190):
    camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
    camada.fill((5, 20, 12, transparencia))
    TELA.blit(camada, (x, y))
    pygame.draw.rect(TELA, VERDE, (x, y, largura, altura), 2, border_radius=14)


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


def desenhar_destaque_capa(tempo):
    """Adiciona brilho e pequenos pontos ao logo, sem criar botoes extras."""
    centro_x = 98
    centro_y = 100
    pulsacao = int(2 + 3 * (0.5 + 0.5 * math.sin(tempo * 0.004)))
    pygame.draw.circle(TELA, (70, 255, 125), (centro_x, centro_y), 39 + pulsacao, 2)
    pygame.draw.circle(TELA, (35, 150, 80), (centro_x, centro_y), 45 + pulsacao, 1)

    for indice in range(8):
        angulo = tempo * 0.0012 + indice * (math.pi / 4)
        distancia = 48 + 4 * math.sin(tempo * 0.003 + indice)
        px = int(centro_x + math.cos(angulo) * distancia)
        py = int(centro_y + math.sin(angulo) * distancia)
        raio = 2 if indice % 2 == 0 else 3
        pygame.draw.circle(TELA, (110, 255, 145), (px, py), raio)


def desenhar_efeito_transformacao(centro_x, centro_y, tempo_restante):
    """Efeito simples de energia verde durante a troca de forma."""
    duracao = 700
    progresso = max(0.0, min(1.0, (duracao - tempo_restante) / duracao))
    pulsacao = 0.5 + 0.5 * math.sin(tempo_restante * 0.035)
    raio_externo = int(34 + progresso * 52 + pulsacao * 7)
    raio_interno = max(18, raio_externo - 20)

    pygame.draw.circle(TELA, (70, 255, 125), (centro_x, centro_y), raio_externo, 3)
    pygame.draw.circle(TELA, (170, 255, 185), (centro_x, centro_y), raio_interno, 2)

    for indice in range(10):
        angulo = indice * (2 * math.pi / 10) + progresso * 2.6
        dentro = raio_interno - 5
        fora = raio_externo + 7
        x1 = int(centro_x + math.cos(angulo) * dentro)
        y1 = int(centro_y + math.sin(angulo) * dentro)
        x2 = int(centro_x + math.cos(angulo) * fora)
        y2 = int(centro_y + math.sin(angulo) * fora)
        pygame.draw.line(TELA, (125, 255, 150), (x1, y1), (x2, y2), 3)
        pygame.draw.circle(TELA, (205, 255, 210), (x2, y2), 3)


def desenhar_coracao(x, y, tamanho, cor):
    """Desenha um coracao simples para representar uma vida."""
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
    pygame.draw.polygon(TELA, cor, pontos)
    pygame.draw.lines(TELA, (255, 195, 195), True, pontos, 2)


def desenhar_vidas(vidas, x=820, y=27):
    for indice in range(3):
        cor = (238, 55, 66) if indice < vidas else (65, 78, 70)
        desenhar_coracao(x + indice * 48, y, 34, cor)


def desenhar_rodape():
    painel(12, 615, 976, 73, 165)
    texto("A/D ou setas: mover   SHIFT: correr   W: pular   S: agachar",
          FONTE_MENOR, BRANCO, 28, 626)
    texto("G: Omnitrix   1/2: aliens   Clique: atacar   SPACE: pausar   ESC: sair",
          FONTE_MENOR, VERDE_CLARO, 28, 653)
    texto("Press Space to Pause Game.", FONTE_MENOR, BRANCO, 770, 590)


# ------------------------------------------------------------
# TELAS INICIAIS
# ------------------------------------------------------------
def tela_nome():
    nome = ""
    digitando = True
    caixa_nome = pygame.Rect(445, 242, 492, 55)
    botao = pygame.Rect(445, 311, 492, 54)
    campo_ativo = True
    hover_anterior = False

    while digitando:
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

        # A capa grafica tem a selva, os dois aliens e os paineis; os dados
        # abaixo sao desenhados em tempo real para manter nome e ranking atuais.
        TELA.blit(CAPA_IMG, (0, 0))
        desenhar_destaque_capa(pygame.time.get_ticks())

        pygame.draw.rect(TELA, (7, 30, 19), caixa_nome, border_radius=13)
        pygame.draw.rect(TELA, VERDE_CLARO if campo_ativo else VERDE,
                         caixa_nome, 2, border_radius=13)
        if nome.strip():
            texto_digitado = nome + ("|" if (pygame.time.get_ticks() // 450) % 2 == 0 else "")
            texto(texto_digitado, FONTE_MEDIA, BRANCO, 465, 255)
        else:
            texto("Clique aqui e digite seu nome", FONTE_PEQUENA,
                  (135, 170, 145), 465, 260)

        brilho = int((math.sin(pygame.time.get_ticks() * 0.005) + 1) * 12)
        cor_botao = (18 + brilho, 92 + brilho, 42 + brilho)
        pygame.draw.rect(TELA, cor_botao, botao, border_radius=13)
        pygame.draw.rect(TELA, VERDE_CLARO if sobre_botao else VERDE,
                         botao, 3, border_radius=13)
        if sobre_botao:
            brilho_x = botao.left + 18 + int((pygame.time.get_ticks() // 8) % (botao.width - 36))
            pygame.draw.line(TELA, (145, 255, 170),
                             (brilho_x, botao.top + 7), (min(brilho_x + 20, botao.right - 5), botao.bottom - 7), 2)
        texto("CONTINUAR  >", FONTE_MEDIA, BRANCO, botao.centerx, botao.centery, True)

        # Preenche o TOP 5 com os resultados reais de log.dat.
        ranking = ler_ranking(5)
        for indice in range(5):
            y_linha = 457 + indice * 29
            linha = pygame.Rect(454, y_linha, 474, 25)
            pygame.draw.rect(TELA, (9, 30, 20), linha, border_radius=6)
            borda_ranking = AMARELO if indice == 0 and indice < len(ranking) else (35, 100, 54)
            pygame.draw.rect(TELA, borda_ranking, linha, 1, border_radius=6)
            if indice < len(ranking):
                registro = ranking[indice]
                nome_ranking = registro["nome"]
                if len(nome_ranking) > 18:
                    nome_ranking = nome_ranking[:17] + "…"
                cor_posicao = AMARELO if indice == 0 else VERDE_CLARO
                texto(str(indice + 1), FONTE_MICRO, cor_posicao, 467, y_linha + 6)
                texto(nome_ranking, FONTE_MICRO, BRANCO, 503, y_linha + 6)
                texto(str(registro["pontos"]), FONTE_MICRO, VERDE_CLARO, 728, y_linha + 6)
                data_hora = registro["data"] + " " + registro["hora"][:5]
                texto(data_hora, FONTE_MICRO, (185, 205, 190), 835, y_linha + 6)
            else:
                texto(str(indice + 1), FONTE_MICRO, (100, 130, 110), 467, y_linha + 6)
                texto("—", FONTE_MICRO, (120, 145, 125), 503, y_linha + 6)
                texto("—", FONTE_MICRO, (120, 145, 125), 728, y_linha + 6)
                texto("—", FONTE_MICRO, (120, 145, 125), 835, y_linha + 6)

        if not ranking:
            texto("Jogue uma partida para aparecer no ranking.", FONTE_MICRO,
                  (150, 180, 155), 690, 604, True)

        pygame.display.flip()
        clock.tick(60)

    return nome.strip()


def tela_boas_vindas(nome):
    ranking = ler_ranking(5)
    botao = pygame.Rect(382, 555, 236, 62)
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
        icone = pygame.transform.smoothscale(OMNITRIX_IMG, (52, 52))
        TELA.blit(icone, (474, 54))
        texto("OMNITRIX RUN", FONTE_TITULO, VERDE_CLARO, 500, 145, True)
        texto("SOBREVIVA A SELVA. DOMINE O OMNITRIX.", FONTE_PEQUENA, BRANCO, 500, 188, True)

        # Cartao esquerdo: boas-vindas, historia e controles.
        painel(72, 205, 410, 325, 205)
        texto("BEM-VINDO,", FONTE_MEDIA, VERDE_CLARO, 102, 230)
        texto(nome[:18], FONTE_GRANDE, BRANCO, 102, 267)
        texto("Sua missao", FONTE_PEQUENA, AMARELO, 102, 326)
        texto("Enfrente as criaturas enviadas pelo vilao", FONTE_MENOR, BRANCO, 102, 352)
        texto("montado no sapo e sobreviva na selva.", FONTE_MENOR, BRANCO, 102, 374)
        texto("COMO JOGAR", FONTE_PEQUENA, VERDE_CLARO, 102, 414)
        texto("• Ratinhos correm pelo chao.", FONTE_MENOR, BRANCO, 102, 440)
        texto("• Morcegos mergulham do alto.", FONTE_MENOR, BRANCO, 102, 462)
        texto("• Os aliens atacam a cada 1,5 segundo.", FONTE_MENOR, BRANCO, 102, 484)
        texto("• Voce tem 3 vidas: ataque e desvie.", FONTE_MENOR, BRANCO, 102, 506)

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
        texto("INICIAR PARTIDA  >", FONTE_MEDIA, BRANCO, botao.centerx, botao.centery, True)
        texto("A/D mover | SHIFT correr | W pular | S agachar",
              FONTE_MENOR, BRANCO, 500, 632, True)
        texto("G Omnitrix | 1 Chamas | 2 Bola | Z/Clique atacar | ESPACO pausa | ESC sair",
              FONTE_MENOR, (190, 210, 195), 500, 654, True)

        pygame.display.flip()
        clock.tick(60)


def desenhar_menu_aliens():
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((0, 0, 0, 205))
    TELA.blit(camada, (0, 0))
    painel(190, 105, 620, 490, 240)
    texto("OMNITRIX", FONTE_TITULO, VERDE_CLARO, 500, 165, True)

    chama = CHAMAS_PARADO_FRAMES[(pygame.time.get_ticks() // 320) % len(CHAMAS_PARADO_FRAMES)]
    bola = BOLA_PARADO_FRAMES[(pygame.time.get_ticks() // 320) % len(BOLA_PARADO_FRAMES)]
    TELA.blit(chama, chama.get_rect(midbottom=(370, 405)))
    TELA.blit(bola, bola.get_rect(midbottom=(630, 405)))
    texto("1 - CHAMAS", FONTE_MEDIA, BRANCO, 370, 420, True)
    texto("2 - BOLA DE CANHAO", FONTE_MEDIA, BRANCO, 620, 420, True)
    texto("0 - VOLTAR AO HEROI", FONTE_PEQUENA, VERDE_CLARO, 500, 490, True)
    texto("Pressione G para fechar", FONTE_PEQUENA, BRANCO, 500, 545, True)


# ------------------------------------------------------------
# PARTIDA
# ------------------------------------------------------------
def jogar(nome):
    jogador_x = 105
    forma = "heroi"
    olhando_esquerda = False

    pontos = 0
    inimigos = []
    morcegos = []
    bolas_de_fogo = []
    tempo_inimigo = 0
    tempo_morcego = 0
    tempo_partida = 0
    vidas = 3
    proximo_disparo_chamas = 0
    proxima_rolagem_bola = 0

    pausa = False
    acabou = False
    selecionando_alien = False

    andando = False
    correndo = False
    pulando = False
    tempo_pulo = 0
    duracao_pulo = 760
    deslocamento_pulo = 0
    abaixado = False
    rolando = False
    tempo_rolagem = 0
    angulo_rolagem = 0
    direcao_rolagem = 1

    ataque_ativo = False
    tempo_ataque = 0
    frame_ataque = 0
    soco_acertou = False

    frame_atual = 0
    tempo_animacao = 0
    nome_animacao = "parado"
    frame_chamas = 0
    tempo_animacao_chamas = 0
    frame_bola = 0
    tempo_animacao_bola = 0
    frame_bola_ataque = 0
    tempo_bola_ataque = 0
    frame_transformacao = 0
    tempo_transformacao = 0
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

                if evento.key == pygame.K_SPACE and not selecionando_alien:
                    pausa = not pausa
                    pausar_musica(pausa)

                elif not pausa and evento.key == pygame.K_g:
                    selecionando_alien = not selecionando_alien
                    tocar_som(SOM_MENU)

                elif not pausa and selecionando_alien:
                    if evento.key == pygame.K_1:
                        forma = "chamas"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 700
                        frame_transformacao = 0
                        tempo_animacao = 0
                        ataque_ativo = False
                        rolando = False
                    elif evento.key == pygame.K_2:
                        forma = "bola"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 700
                        frame_transformacao = 0
                        tempo_animacao = 0
                        ataque_ativo = False
                        rolando = False
                    elif evento.key == pygame.K_0:
                        forma = "heroi"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 700
                        frame_transformacao = 0
                        tempo_animacao = 0
                        ataque_ativo = False
                        rolando = False

                elif not pausa and not selecionando_alien:
                    if evento.key in (pygame.K_w, pygame.K_UP) and not pulando and not abaixado and not rolando:
                        pulando = True
                        tempo_pulo = 0
                        abaixado = False
                        tocar_som(SOM_PULO)
                    elif evento.key in (pygame.K_s, pygame.K_DOWN) and not pulando and not rolando:
                        abaixado = True
                    elif forma == "heroi" and evento.key == pygame.K_z and not ataque_ativo and not pulando and not rolando:
                        ataque_ativo = True
                        tempo_ataque = 0
                        frame_ataque = 0
                        soco_acertou = False
                        tocar_som(SOM_SOCO)
                    elif forma == "chamas" and evento.key == pygame.K_z and not abaixado and not pulando and tempo >= proximo_disparo_chamas:
                        bolas_de_fogo.append(criar_bola_fogo(jogador_x, olhando_esquerda, deslocamento_pulo))
                        proximo_disparo_chamas = tempo + COOLDOWN_CHAMAS
                        tocar_som(SOM_TIRO)
                    elif forma == "bola" and evento.key == pygame.K_z and not rolando and not pulando and tempo >= proxima_rolagem_bola:
                        rolando = True
                        tempo_rolagem = 700
                        angulo_rolagem = 0
                        direcao_rolagem = -1 if olhando_esquerda else 1
                        proxima_rolagem_bola = tempo + COOLDOWN_BOLA
                        invulneravel = 90
                        tocar_som(SOM_ROLAGEM)

            if evento.type == pygame.KEYUP:
                if evento.key in (pygame.K_s, pygame.K_DOWN):
                    abaixado = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not pausa and not selecionando_alien:
                if forma == "heroi" and not ataque_ativo and not pulando and not rolando:
                    ataque_ativo = True
                    tempo_ataque = 0
                    frame_ataque = 0
                    soco_acertou = False
                    tocar_som(SOM_SOCO)
                elif forma == "bola" and not rolando and not pulando and tempo >= proxima_rolagem_bola:
                    rolando = True
                    tempo_rolagem = 700
                    angulo_rolagem = 0
                    direcao_rolagem = -1 if olhando_esquerda else 1
                    proxima_rolagem_bola = tempo + COOLDOWN_BOLA
                    invulneravel = 90
                    tocar_som(SOM_ROLAGEM)
                elif forma == "chamas" and not abaixado and not pulando and tempo >= proximo_disparo_chamas:
                    bolas_de_fogo.append(criar_bola_fogo(jogador_x, olhando_esquerda, deslocamento_pulo))
                    proximo_disparo_chamas = tempo + COOLDOWN_CHAMAS
                    tocar_som(SOM_TIRO)

        # ATUALIZACAO DO JOGO
        if not pausa and not selecionando_alien:
            tempo_partida += dt
            teclas = pygame.key.get_pressed()
            andando = False
            correndo = False

            if tempo_transformacao > 0:
                tempo_transformacao -= dt
                tempo_animacao += dt
                if tempo_animacao >= 85:
                    frame_transformacao = (frame_transformacao + 1) % len(ANIMACAO_TRANSFORMAR)
                    tempo_animacao = 0

            if pulando:
                tempo_pulo += dt
                progresso_pulo = tempo_pulo / duracao_pulo
                deslocamento_pulo = int(ALTURA_PULO * math.sin(min(1, progresso_pulo) * math.pi))
                if tempo_pulo >= duracao_pulo:
                    pulando = False
                    tempo_pulo = 0
                    deslocamento_pulo = 0
            else:
                deslocamento_pulo = 0

            if rolando:
                tempo_rolagem -= dt
                jogador_x += 12 * direcao_rolagem
                angulo_rolagem += 0.50 * dt * direcao_rolagem
                if tempo_rolagem <= 0 or jogador_x < 0 or jogador_x > 650:
                    rolando = False
                invulneravel = 90

            elif not pulando and not abaixado and not ataque_ativo:
                velocidade = 5
                if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]:
                    velocidade = 9
                    correndo = True

                # O jogador anda no eixo X. Durante o pulo ele nao anda para os lados.
                if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                    jogador_x -= velocidade
                    olhando_esquerda = True
                    andando = True
                if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                    jogador_x += velocidade
                    olhando_esquerda = False
                    andando = True

            if jogador_x < 20:
                jogador_x = 20
            if jogador_x > 660:
                jogador_x = 660

            # TAMANHO DA AREA DE COLISAO DO PERSONAGEM
            if forma == "bola":
                jogador_largura = 108
                jogador_altura = 88
            elif forma == "chamas":
                jogador_largura = 82
                jogador_altura = 125
            else:
                jogador_largura = 74
                jogador_altura = 116

            if abaixado:
                jogador_altura = 76

            jogador = pygame.Rect(
                int(jogador_x), CHAO - jogador_altura - deslocamento_pulo,
                jogador_largura, jogador_altura
            )

            # ANIMACAO DO HEROI: PARADO, CAMINHANDO OU CORRENDO
            if forma == "heroi" and not ataque_ativo and not pulando and not abaixado and not rolando and tempo_transformacao <= 0:
                if andando:
                    if correndo:
                        if nome_animacao != "correr":
                            nome_animacao = "correr"
                            frame_atual = 0
                            tempo_animacao = 0
                        tempo_frame = 85
                        animacao_atual = ANIMACAO_CORRER
                    else:
                        if nome_animacao != "caminhar":
                            nome_animacao = "caminhar"
                            frame_atual = 0
                            tempo_animacao = 0
                        tempo_frame = 135
                        animacao_atual = ANIMACAO_CAMINHAR
                    tempo_animacao += dt
                    if tempo_animacao >= tempo_frame:
                        frame_atual = (frame_atual + 1) % len(animacao_atual)
                        tempo_animacao = 0
                else:
                    nome_animacao = "parado"
                    frame_atual = 0
                    tempo_animacao = 0

            # Corrida possui quadros proprios; o repouso anima em velocidade menor.
            if forma == "chamas" and andando and tempo_transformacao <= 0:
                tempo_animacao_chamas += dt
                if tempo_animacao_chamas >= 105:
                    frame_chamas = (frame_chamas + 1) % len(CHAMAS_CORRER_FRAMES)
                    tempo_animacao_chamas = 0
            elif forma != "chamas":
                frame_chamas = 0
                tempo_animacao_chamas = 0

            if forma == "bola" and tempo_transformacao <= 0:
                if rolando:
                    tempo_bola_ataque += dt
                    if tempo_bola_ataque >= 75:
                        frame_bola_ataque = (frame_bola_ataque + 1) % len(BOLA_ATACAR_FRAMES)
                        tempo_bola_ataque = 0
                elif andando and not pulando and not abaixado:
                    tempo_animacao_bola += dt
                    intervalo_bola = 85 if correndo else 135
                    if tempo_animacao_bola >= intervalo_bola:
                        frame_bola = (frame_bola + 1) % 6
                        tempo_animacao_bola = 0
                else:
                    tempo_animacao_bola = 0
                    tempo_bola_ataque = 0
            elif forma != "bola":
                frame_bola = 0
                frame_bola_ataque = 0
                tempo_animacao_bola = 0
                tempo_bola_ataque = 0

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

            # MOVIMENTO DAS BOLAS DE FOGO
            for fogo in bolas_de_fogo[:]:
                fogo[0].x += fogo[1]
                if fogo[0].right < 0 or fogo[0].left > LARGURA:
                    bolas_de_fogo.remove(fogo)

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

            # Morcegos surgem no alto e mergulham em direcao ao jogador.
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
                    y_morcego = random.randint(65, 205)
                    morcegos.append([float(x_morcego), float(y_morcego), 0, 0])
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

                # Chamas destroi o ratinho quando a bola de fogo encosta nele.
                atingido_pelo_fogo = False
                for fogo in bolas_de_fogo[:]:
                    if fogo[0].colliderect(rat_rect):
                        bolas_de_fogo.remove(fogo)
                        if inimigo in inimigos:
                            inimigos.remove(inimigo)
                        pontos += 15
                        tocar_som(SOM_IMPACTO)
                        tocar_som(SOM_PONTO)
                        atingido_pelo_fogo = True
                        break
                if atingido_pelo_fogo:
                    continue

                # Bola de Canhao elimina os ratinhos enquanto esta rolando.
                if rolando and forma == "bola" and jogador.colliderect(rat_rect):
                    if inimigo in inimigos:
                        inimigos.remove(inimigo)
                    pontos += 20
                    tocar_som(SOM_IMPACTO)
                    tocar_som(SOM_PONTO)
                    continue

                # Contato com um ratinho tira uma vida. O jogador ganha um breve
                # periodo de protecao para nao perder varias vidas no mesmo instante.
                area_jogador = pygame.Rect(jogador.centerx - 30, jogador.bottom - 78, 60, 72)
                area_ratinho = pygame.Rect(int(inimigo[0]) + 12, int(inimigo[1]) + 8, 88, 60)
                if (area_jogador.colliderect(area_ratinho)
                        and not pulando and not abaixado and not rolando and invulneravel <= 0):
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
                alvo_x = jogador.centerx - 48
                alvo_y = CHAO - 120
                diferenca_x = alvo_x - morcego[0]
                diferenca_y = alvo_y - morcego[1]
                distancia = math.sqrt(diferenca_x * diferenca_x + diferenca_y * diferenca_y)
                if distancia > 0:
                    morcego[0] += (diferenca_x / distancia) * velocidade_morcegos
                    morcego[1] += (diferenca_y / distancia) * velocidade_morcegos

                morcego[3] += dt
                if morcego[3] >= 105:
                    morcego[2] = (morcego[2] + 1) % len(MORCEGO_FRAMES)
                    morcego[3] = 0

                bat_rect = pygame.Rect(int(morcego[0]) + 20, int(morcego[1]) + 20, 76, 54)

                # A bola de fogo tambem elimina morcegos.
                morcego_atingido = False
                for fogo in bolas_de_fogo[:]:
                    if fogo[0].colliderect(bat_rect):
                        bolas_de_fogo.remove(fogo)
                        if morcego in morcegos:
                            morcegos.remove(morcego)
                        pontos += 20
                        tocar_som(SOM_IMPACTO)
                        tocar_som(SOM_PONTO)
                        morcego_atingido = True
                        break
                if morcego_atingido:
                    continue

                # Bola de Canhao pode atingir os morcegos durante a rolada.
                if rolando and forma == "bola" and jogador.colliderect(bat_rect):
                    if morcego in morcegos:
                        morcegos.remove(morcego)
                    pontos += 20
                    tocar_som(SOM_IMPACTO)
                    tocar_som(SOM_PONTO)
                    continue

                # O contato com o morcego tira uma vida, respeitando a invulnerabilidade.
                if jogador.colliderect(bat_rect):
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

                if morcego[0] < -130 or morcego[1] > CHAO - 25:
                    if morcego in morcegos:
                        morcegos.remove(morcego)

        # ----------------------------------------------------
        # DESENHO DA CENA
        # ----------------------------------------------------
        TELA.blit(FUNDO, (0, 0))
        desenhar_sol(tempo)
        TELA.blit(DECORACAO_IMG, (int(decor_x), int(decor_y)))

        # Chefe fixo no outro lado da tela, atras dos ratinhos.
        boss_rect = BOSS_IMG.get_rect(midbottom=(830, CHAO + 4))
        TELA.blit(BOSS_IMG, boss_rect)

        for inimigo in inimigos:
            imagem_rat = RATINHO_FRAMES[inimigo[3]]
            TELA.blit(imagem_rat, (int(inimigo[0]), int(inimigo[1])))

        for morcego in morcegos:
            imagem_morcego = MORCEGO_FRAMES[morcego[2]]
            TELA.blit(imagem_morcego, (int(morcego[0]), int(morcego[1])))

        # Escolha do frame do jogador.
        deslocamento_pulo_visual = deslocamento_pulo
        if tempo_transformacao > 0:
            # A sequencia verde do Omnitrix aparece antes de revelar a nova forma.
            imagem_jogador = ANIMACAO_TRANSFORMAR[frame_transformacao]
            imagem_jogador = pygame.transform.smoothscale(imagem_jogador, (132, 124))
        elif forma == "heroi":
            if ataque_ativo:
                imagem_jogador = ANIMACAO_ATACAR[min(frame_ataque, len(ANIMACAO_ATACAR)-1)]
            elif pulando:
                indice_pulo = min(len(ANIMACAO_PULAR)-1, int((tempo_pulo / duracao_pulo) * len(ANIMACAO_PULAR)))
                imagem_jogador = ANIMACAO_PULAR[indice_pulo]
            elif abaixado:
                indice_agachar = (tempo // 150) % len(ANIMACAO_AGACHAR)
                imagem_jogador = ANIMACAO_AGACHAR[indice_agachar]
            elif rolando:
                indice_rolar = (tempo // 85) % len(ANIMACAO_ROLAR)
                imagem_jogador = ANIMACAO_ROLAR[indice_rolar]
            elif nome_animacao == "correr":
                imagem_jogador = ANIMACAO_CORRER[frame_atual]
            elif nome_animacao == "caminhar":
                imagem_jogador = ANIMACAO_CAMINHAR[frame_atual]
            else:
                imagem_jogador = ANIMACAO_CAMINHAR[0]

            tamanho = (132, 124)
            if abaixado:
                tamanho = (132, 92)
            imagem_jogador = pygame.transform.smoothscale(imagem_jogador, tamanho)

        elif forma == "chamas":
            if andando:
                imagem_jogador = CHAMAS_CORRER_FRAMES[frame_chamas]
            else:
                indice_parado = (tempo // 340) % len(CHAMAS_PARADO_FRAMES)
                imagem_jogador = CHAMAS_PARADO_FRAMES[indice_parado]
                deslocamento_pulo_visual = deslocamento_pulo + int(1 * math.sin(tempo * 0.004))

        else:
            # A Bola usa sempre o mesmo conjunto de sprites: repouso, andar,
            # corrida, pulo, agachamento e ataque sao variacoes do mesmo modelo.
            if rolando:
                indice_ataque_bola = frame_bola_ataque % len(BOLA_ATACAR_FRAMES)
                imagem_jogador = BOLA_ATACAR_FRAMES[indice_ataque_bola]
                deslocamento_pulo_visual = deslocamento_pulo
            elif pulando:
                indice_pulo_bola = min(
                    len(BOLA_PULAR_FRAMES) - 1,
                    int((tempo_pulo / duracao_pulo) * len(BOLA_PULAR_FRAMES))
                )
                imagem_jogador = BOLA_PULAR_FRAMES[indice_pulo_bola]
            elif abaixado:
                indice_agachar_bola = (tempo // 150) % len(BOLA_AGACHAR_FRAMES)
                imagem_jogador = BOLA_AGACHAR_FRAMES[indice_agachar_bola]
            elif andando and correndo:
                indice_correr_bola = (tempo // 85) % len(BOLA_CORRER_FRAMES)
                imagem_jogador = BOLA_CORRER_FRAMES[indice_correr_bola]
            elif andando:
                indice_andar_bola = (tempo // 135) % len(BOLA_CAMINHAR_FRAMES)
                imagem_jogador = BOLA_CAMINHAR_FRAMES[indice_andar_bola]
            else:
                indice_parado_bola = (tempo // 420) % len(BOLA_PARADO_FRAMES)
                imagem_jogador = BOLA_PARADO_FRAMES[indice_parado_bola]
                deslocamento_pulo_visual = deslocamento_pulo + int(1 * abs(math.sin(tempo * 0.006)))

        if olhando_esquerda:
            imagem_jogador = pygame.transform.flip(imagem_jogador, True, False)

        posicao_jogador = imagem_jogador.get_rect(
            midbottom=(int(jogador.centerx), CHAO - deslocamento_pulo_visual)
        )
        if forma == "bola" and rolando:
            lado_rastro = 1 if olhando_esquerda else -1
            for linha in range(3):
                inicio_rastro = (posicao_jogador.centerx + lado_rastro * (42 + linha * 9),
                                 posicao_jogador.centery - 18 + linha * 17)
                fim_rastro = (inicio_rastro[0] + lado_rastro * 24, inicio_rastro[1])
                pygame.draw.line(TELA, (85, 255, 135), inicio_rastro, fim_rastro, 3)
        # Pisca por um instante depois de sofrer dano, indicando invulnerabilidade.
        mostrar_jogador = not (invulneravel > 0 and (tempo // 100) % 2 == 0)
        if mostrar_jogador:
            TELA.blit(imagem_jogador, posicao_jogador)

        for fogo in bolas_de_fogo:
            imagem_fogo = BOLA_FOGO_IMG if fogo[1] > 0 else BOLA_FOGO_ESQUERDA_IMG
            TELA.blit(imagem_fogo, fogo[0])

        # Interface: pontuacao e tres coracoes para mostrar as vidas.
        painel(12, 12, 355, 58, 190)
        icone_hud = pygame.transform.smoothscale(OMNITRIX_IMG, (46, 46))
        TELA.blit(icone_hud, (20, 18))
        texto("Pontos: " + str(pontos), FONTE_MEDIA, BRANCO, 78, 26)
        painel(810, 12, 178, 58, 190)
        texto("VIDAS", FONTE_MENOR, BRANCO, 822, 14)
        desenhar_vidas(vidas, 820, 31)
        nome_forma = "HEROI" if forma == "heroi" else "CHAMAS" if forma == "chamas" else "BOLA DE CANHAO"
        texto("Forma: " + nome_forma, FONTE_PEQUENA, VERDE_CLARO, 20, 575)
        if forma == "chamas":
            tempo_restante = max(0, proximo_disparo_chamas - tempo) / 1000
            if tempo_restante <= 0:
                texto("Bola de fogo: PRONTA", FONTE_MENOR, VERDE_CLARO, 20, 594)
            else:
                texto("Bola de fogo: " + str(round(tempo_restante, 1)) + "s", FONTE_MENOR, BRANCO, 20, 594)
        elif forma == "bola":
            tempo_restante = max(0, proxima_rolagem_bola - tempo) / 1000
            if tempo_restante <= 0:
                texto("Rolagem: PRONTA", FONTE_MENOR, VERDE_CLARO, 20, 594)
            else:
                texto("Rolagem: " + str(round(tempo_restante, 1)) + "s", FONTE_MENOR, BRANCO, 20, 594)
        desenhar_rodape()

        if tempo_transformacao > 0:
            desenhar_efeito_transformacao(
                jogador.centerx, CHAO - 78 - deslocamento_pulo, tempo_transformacao
            )

        if selecionando_alien:
            desenhar_menu_aliens()

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
