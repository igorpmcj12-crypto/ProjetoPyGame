import pygame
import random
import math
import os
from datetime import datetime
from Recursos.trabalho import criar_inimigo, mover_decoracao

pygame.init()

LARGURA = 1000
ALTURA = 700
CHAO = 560
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Omnitrix Run")

# O jogo continua funcionando mesmo se o computador nao tiver audio disponivel.
try:
    pygame.mixer.init()
except pygame.error:
    pass

BASE = "bases"
FONTE_PATH = os.path.join(BASE, "fontes", "DejaVuSans-Bold.ttf")


def fonte(tamanho):
    if os.path.exists(FONTE_PATH):
        return pygame.font.Font(FONTE_PATH, tamanho)
    return pygame.font.SysFont("Arial", tamanho, bold=True)


FONTE_GRANDE = fonte(48)
FONTE_MEDIA = fonte(30)
FONTE_PEQUENA = fonte(18)
FONTE_TITULO = fonte(64)


def carregar_imagem(caminho):
    return pygame.image.load(caminho).convert_alpha()


def carregar_animacao(nome, quantidade):
    imagens = []
    for numero in range(1, quantidade + 1):
        caminho = os.path.join(BASE, "imagens", "animacoes", nome,
                               nome + "_" + str(numero).zfill(2) + ".png")
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


FUNDO = pygame.image.load(os.path.join(BASE, "imagens", "fundo.png")).convert()
CAPA_IMG = carregar_imagem(os.path.join(BASE, "imagens", "capa.png"))
OMNITRIX_IMG = carregar_imagem(os.path.join(BASE, "imagens", "icone_omnitrix.png"))
INIMIGO_IMG = carregar_imagem(os.path.join(BASE, "imagens", "inimigo.png"))
DECORACAO_IMG = carregar_imagem(os.path.join(BASE, "imagens", "decoracao.png"))

ANIMACAO_CAMINHAR = carregar_animacao("caminhar", 6)
ANIMACAO_CORRER = carregar_animacao("correr", 6)
ANIMACAO_ATACAR = carregar_animacao("atacar", 4)
ANIMACAO_PULAR = carregar_animacao("pular", 4)
ANIMACAO_ROLAR = carregar_animacao("rolar", 6)
ANIMACAO_MORRER = carregar_animacao("morrer", 6)
ANIMACAO_TRANSFORMAR = carregar_animacao("transformar", 8)
ANIMACAO_AGACHAR = carregar_animacao("agachar", 4)

ALIEN_CHAMAS_IMG = carregar_imagem(os.path.join(BASE, "imagens", "aliens", "chamas.png"))
ALIEN_BOLA_IMG = carregar_imagem(os.path.join(BASE, "imagens", "aliens", "bola_de_canhao.png"))

SOM_PONTO = carregar_som("ponto.wav")
SOM_MORTE = carregar_som("morte.wav")
SOM_SOCO = carregar_som("soco.wav")
SOM_TIRO = carregar_som("tiro.wav")
SOM_IMPACTO = carregar_som("impacto.wav")
SOM_TRANSFORMACAO = carregar_som("transformacao.wav")
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

PRETO = (8, 10, 12)
BRANCO = (240, 245, 240)
VERDE = (70, 220, 110)
VERDE_CLARO = (130, 255, 150)
VERMELHO = (230, 80, 80)
AMARELO = (255, 220, 70)
clock = pygame.time.Clock()


def texto(conteudo, fonte_usada, cor, x, y, centro=False):
    imagem = fonte_usada.render(conteudo, True, cor)
    retangulo = imagem.get_rect()
    if centro:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    TELA.blit(imagem, retangulo)


def ler_recorde():
    maior = 0
    nome = "Ninguem"
    data = "--/--/----"
    hora = "--:--:--"
    if os.path.exists("log.dat"):
        with open("log.dat", "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                partes = linha.strip().split("|")
                if len(partes) == 4:
                    try:
                        pontos = int(partes[1])
                        if pontos > maior:
                            maior = pontos
                            nome = partes[0]
                            data = partes[2]
                            hora = partes[3]
                    except ValueError:
                        pass
    return nome, maior, data, hora


def salvar_log(nome, pontos):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    with open("log.dat", "a", encoding="utf-8") as arquivo:
        arquivo.write(nome + "|" + str(pontos) + "|" + data + "|" + hora + "\n")


def falar(texto_fala):
    try:
        import pyttsx3
        voz = pyttsx3.init()
        voz.say(texto_fala)
        voz.runAndWait()
        voz.stop()
    except Exception:
        pass


def tela_nome():
    nome = ""
    digitando = True
    capa = pygame.transform.smoothscale(CAPA_IMG, (310, 578))
    moldura_capa = pygame.Rect(625, 45, 340, 610)

    while digitando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                if evento.key == pygame.K_RETURN and nome.strip() != "":
                    digitando = False
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif len(nome) < 18 and evento.unicode.isprintable():
                    nome += evento.unicode

        TELA.blit(FUNDO, (0, 0))
        pygame.draw.rect(TELA, (8, 24, 17), (45, 55, 545, 600), border_radius=22)
        pygame.draw.rect(TELA, VERDE, (45, 55, 545, 600), 3, border_radius=22)
        icone_menu = pygame.transform.smoothscale(OMNITRIX_IMG, (76, 76))
        TELA.blit(icone_menu, (279, 92))
        texto("OMNITRIX RUN", FONTE_GRANDE, VERDE_CLARO, 317, 215, True)
        texto("A aventura começa aqui", FONTE_PEQUENA, BRANCO, 317, 270, True)
        texto("Digite seu nome:", FONTE_MEDIA, BRANCO, 317, 360, True)
        pygame.draw.rect(TELA, (20, 45, 30), (105, 405, 425, 62), border_radius=10)
        pygame.draw.rect(TELA, VERDE, (105, 405, 425, 62), 2, border_radius=10)
        texto(nome + "_", FONTE_MEDIA, BRANCO, 125, 419)
        texto("ENTER para continuar", FONTE_PEQUENA, VERDE_CLARO, 317, 520, True)
        texto("ESC para fechar", FONTE_PEQUENA, BRANCO, 317, 558, True)
        pygame.draw.rect(TELA, (235, 245, 235), moldura_capa, border_radius=18)
        pygame.draw.rect(TELA, VERDE, moldura_capa, 4, border_radius=18)
        TELA.blit(capa, (640, 61))
        pygame.display.flip()
        clock.tick(60)
    return nome.strip()


def tela_boas_vindas(nome):
    recorde_nome, recorde_pontos, recorde_data, recorde_hora = ler_recorde()
    botao = pygame.Rect(390, 510, 220, 65)
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao.collidepoint(evento.pos):
                    return
        TELA.blit(FUNDO, (0, 0))
        texto("BEM-VINDO", FONTE_TITULO, VERDE_CLARO, LARGURA//2, 100, True)
        texto(nome, FONTE_GRANDE, BRANCO, LARGURA//2, 170, True)
        texto("Mecânica:", FONTE_MEDIA, VERDE, 180, 245)
        texto("A/D ou setas: andar | SHIFT: correr", FONTE_PEQUENA, BRANCO, 180, 285)
        texto("W ou seta para cima: pular | S ou seta para baixo: agachar", FONTE_PEQUENA, BRANCO, 180, 315)
        texto("G: escolher alien | botão esquerdo: ataque", FONTE_PEQUENA, BRANCO, 180, 345)
        texto("SPACE: pausar | ESC: fechar", FONTE_PEQUENA, BRANCO, 180, 375)
        pygame.draw.rect(TELA, VERDE, botao, border_radius=12)
        texto("INICIAR", FONTE_MEDIA, PRETO, botao.centerx, botao.centery, True)
        texto("Maior pontuacao: " + recorde_nome + " - " + str(recorde_pontos),
              FONTE_PEQUENA, BRANCO, LARGURA//2, 610, True)
        texto("Partida: " + recorde_data + " " + recorde_hora,
              FONTE_PEQUENA, BRANCO, LARGURA//2, 640, True)
        pygame.display.flip()
        clock.tick(60)


def desenhar_sol(t):
    raio = 34 + int(8 * math.sin(t * 0.002))
    pygame.draw.circle(TELA, AMARELO, (LARGURA - 55, 55), raio)


def desenhar_menu_aliens():
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((0, 0, 0, 205))
    TELA.blit(camada, (0, 0))
    painel = pygame.Rect(225, 120, 550, 460)
    pygame.draw.rect(TELA, (9, 28, 18), painel, border_radius=18)
    pygame.draw.rect(TELA, VERDE, painel, 4, border_radius=18)
    texto("OMNITRIX", FONTE_TITULO, VERDE_CLARO, LARGURA//2, 175, True)
    chama = pygame.transform.smoothscale(ALIEN_CHAMAS_IMG, (95, 145))
    bola = pygame.transform.smoothscale(ALIEN_BOLA_IMG, (150, 120))
    TELA.blit(chama, (330, 250))
    TELA.blit(bola, (530, 260))
    texto("1 - CHAMAS", FONTE_MEDIA, BRANCO, 375, 420, True)
    texto("2 - BOLA DE CANHÃO", FONTE_MEDIA, BRANCO, 605, 420, True)
    texto("0 - VOLTAR AO HERÓI", FONTE_PEQUENA, VERDE_CLARO, LARGURA//2, 500, True)
    texto("G fecha o menu", FONTE_PEQUENA, BRANCO, LARGURA//2, 545, True)


def jogar(nome):
    jogador_x = 120
    jogador_largura = 75
    jogador_altura = 125
    jogador = pygame.Rect(jogador_x, CHAO - jogador_altura, jogador_largura, jogador_altura)

    inimigos = []
    pontos = 0
    tempo_inimigo = 0
    pausa = False
    acabou = False
    selecionando_alien = False
    forma = "heroi"

    frame_atual = 0
    tempo_animacao = 0
    nome_animacao = "parado"
    ataque_ativo = False
    tempo_ataque = 0
    frame_ataque = 0
    soco_acertou = False
    aviso_ataque = 0
    olhando_esquerda = False

    pulando = False
    tempo_pulo = 0
    duracao_pulo = 650
    abaixado = False
    rolando = False
    tempo_rolagem = 0
    angulo_rolagem = 0
    invulneravel = 0
    tempo_transformacao = 0

    decor_x = 700
    decor_y = 180
    decor_vx = 2
    decor_vy = 1

    while not acabou:
        dt = clock.tick(60)
        tempo = pygame.time.get_ticks()

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

                if not pausa and evento.key == pygame.K_g:
                    selecionando_alien = not selecionando_alien

                elif not pausa and selecionando_alien:
                    if evento.key == pygame.K_1:
                        forma = "chamas"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 450
                        ataque_ativo = False
                        rolando = False
                    elif evento.key == pygame.K_2:
                        forma = "bola"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 450
                        ataque_ativo = False
                        rolando = False
                    elif evento.key == pygame.K_0:
                        forma = "heroi"
                        tocar_som(SOM_TRANSFORMACAO)
                        selecionando_alien = False
                        tempo_transformacao = 450
                        ataque_ativo = False
                        rolando = False

                elif not pausa and not selecionando_alien:
                    if evento.key in (pygame.K_w, pygame.K_UP) and not pulando and not abaixado and not rolando:
                        pulando = True
                        tempo_pulo = 0
                        frame_atual = 0
                    if evento.key in (pygame.K_s, pygame.K_DOWN) and not pulando and not rolando:
                        abaixado = True
                    if forma == "heroi" and evento.key == pygame.K_z and not ataque_ativo and not rolando:
                        ataque_ativo = True
                        tempo_ataque = 0
                        frame_ataque = 0
                        soco_acertou = False
                        tocar_som(SOM_SOCO)

            if evento.type == pygame.KEYUP:
                if evento.key in (pygame.K_s, pygame.K_DOWN):
                    abaixado = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not pausa and not selecionando_alien:
                if forma == "heroi" and not ataque_ativo and not rolando:
                    ataque_ativo = True
                    tempo_ataque = 0
                    frame_ataque = 0
                    soco_acertou = False
                    tocar_som(SOM_SOCO)
                elif forma == "bola" and not rolando and not pulando:
                    rolando = True
                    tempo_rolagem = 650
                    angulo_rolagem = 0
                elif forma == "chamas":
                    aviso_ataque = 2200
                    tocar_som(SOM_TIRO)

        if not pausa and not selecionando_alien:
            teclas = pygame.key.get_pressed()
            andando = False
            correndo = False

            if tempo_transformacao > 0:
                tempo_transformacao -= dt

            if pulando:
                tempo_pulo += dt
                if tempo_pulo >= duracao_pulo:
                    pulando = False
                    tempo_pulo = 0

            if rolando:
                tempo_rolagem -= dt
                jogador_x += 12
                angulo_rolagem = (angulo_rolagem + 24) % 360
                if tempo_rolagem <= 0 or jogador_x > LARGURA - 100:
                    rolando = False
                if forma == "bola":
                    invulneravel = 80
            elif not pulando and not abaixado and not ataque_ativo:
                velocidade = 6
                if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]:
                    correndo = True
                    velocidade = 10
                if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                    andando = True
                    jogador_x -= velocidade
                    olhando_esquerda = True
                if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                    andando = True
                    jogador_x += velocidade
                    olhando_esquerda = False

            if jogador_x < 0:
                jogador_x = 0
            if jogador_x > LARGURA - jogador_largura:
                jogador_x = LARGURA - jogador_largura

            if pulando:
                progresso_pulo = tempo_pulo / duracao_pulo
                deslocamento_pulo = int(55 * math.sin(progresso_pulo * math.pi))
            else:
                deslocamento_pulo = 0

            if forma == "bola":
                jogador_largura = 110
                jogador_altura = 95
            elif forma == "chamas":
                jogador_largura = 75
                jogador_altura = 135
            else:
                jogador_largura = 75
                jogador_altura = 125

            if abaixado:
                jogador_altura = int(jogador_altura * 0.68)

            jogador = pygame.Rect(int(jogador_x), CHAO - jogador_altura - deslocamento_pulo,
                                  jogador_largura, jogador_altura)

            if forma == "heroi" and not ataque_ativo and not pulando and not abaixado and not rolando:
                if andando:
                    if correndo:
                        if nome_animacao != "correr":
                            nome_animacao = "correr"
                            frame_atual = 0
                            tempo_animacao = 0
                        animacao_movimento = ANIMACAO_CORRER
                        velocidade_frame = 85
                    else:
                        if nome_animacao != "caminhar":
                            nome_animacao = "caminhar"
                            frame_atual = 0
                            tempo_animacao = 0
                        animacao_movimento = ANIMACAO_CAMINHAR
                        velocidade_frame = 140
                    tempo_animacao += dt
                    if tempo_animacao >= velocidade_frame:
                        frame_atual = (frame_atual + 1) % len(animacao_movimento)
                        tempo_animacao = 0
                else:
                    nome_animacao = "parado"
                    frame_atual = 0
                    tempo_animacao = 0

            if ataque_ativo:
                tempo_ataque += dt
                if tempo_ataque >= 95:
                    frame_ataque += 1
                    tempo_ataque = 0
                    if frame_ataque >= len(ANIMACAO_ATACAR):
                        ataque_ativo = False
                        frame_ataque = 0

                # O soco so causa dano uma vez por ataque, a curta distancia.
                if not soco_acertou and frame_ataque >= 2:
                    if olhando_esquerda:
                        area_soco = pygame.Rect(jogador.left - 48, jogador.top + 15, 55, jogador.height - 25)
                    else:
                        area_soco = pygame.Rect(jogador.right - 5, jogador.top + 15, 55, jogador.height - 25)
                    for inimigo in inimigos[:]:
                        inimigo_rect = INIMIGO_IMG.get_rect(topleft=(inimigo[0], inimigo[1]))
                        if area_soco.colliderect(inimigo_rect):
                            inimigos.remove(inimigo)
                            pontos += 10
                            soco_acertou = True
                            tocar_som(SOM_IMPACTO)
                            tocar_som(SOM_PONTO)
                            break

            if invulneravel > 0:
                invulneravel -= dt

            decor_x, decor_y, decor_vx, decor_vy = mover_decoracao(
                decor_x, decor_y, decor_vx, decor_vy, LARGURA, ALTURA
            )

            tempo_inimigo += dt
            if tempo_inimigo >= 900:
                # Todos os inimigos surgem na mesma altura do chao do personagem.
                y_inimigo = CHAO - INIMIGO_IMG.get_height()
                inimigos.append(criar_inimigo(LARGURA, y_inimigo))
                tempo_inimigo = 0

            for inimigo in inimigos[:]:
                inimigo[0] -= inimigo[2]
                if inimigo[0] < -80:
                    inimigos.remove(inimigo)
                    continue

                inimigo_rect = INIMIGO_IMG.get_rect(topleft=(int(inimigo[0]), int(inimigo[1])))

                if rolando and forma == "bola" and jogador.colliderect(inimigo_rect):
                    if inimigo in inimigos:
                        inimigos.remove(inimigo)
                        pontos += 20
                        tocar_som(SOM_IMPACTO)
                        tocar_som(SOM_PONTO)
                elif jogador.colliderect(inimigo_rect) and not abaixado and not pulando and not invulneravel:
                    tocar_som(SOM_MORTE)
                    acabou = True

            if aviso_ataque > 0:
                aviso_ataque -= dt

        TELA.blit(FUNDO, (0, 0))
        desenhar_sol(tempo)
        TELA.blit(DECORACAO_IMG, (int(decor_x), int(decor_y)))

        # Seleciona o desenho e o movimento atual sem usar classes.
        if forma == "heroi":
            if ataque_ativo:
                imagem_jogador = ANIMACAO_ATACAR[frame_ataque]
            elif pulando:
                indice_pulo = min(3, int((tempo_pulo / duracao_pulo) * 4))
                imagem_jogador = ANIMACAO_PULAR[indice_pulo]
            elif abaixado:
                indice_agachar = (pygame.time.get_ticks() // 130) % len(ANIMACAO_AGACHAR)
                imagem_jogador = ANIMACAO_AGACHAR[indice_agachar]
            elif nome_animacao == "correr":
                imagem_jogador = ANIMACAO_CORRER[frame_atual]
            elif nome_animacao == "caminhar":
                imagem_jogador = ANIMACAO_CAMINHAR[frame_atual]
            else:
                imagem_jogador = ANIMACAO_CAMINHAR[0]
        elif forma == "chamas":
            imagem_jogador = ALIEN_CHAMAS_IMG
            if andando:
                angulo = math.sin(tempo * 0.018) * 3
                imagem_jogador = pygame.transform.rotate(imagem_jogador, angulo)
        else:
            imagem_jogador = ALIEN_BOLA_IMG
            if rolando:
                imagem_jogador = pygame.transform.rotate(imagem_jogador, angulo_rolagem)
            elif andando:
                angulo = math.sin(tempo * 0.018) * 3
                imagem_jogador = pygame.transform.rotate(imagem_jogador, angulo)

        if forma == "heroi":
            if abaixado:
                tamanho = (imagem_jogador.get_width(), max(40, int(imagem_jogador.get_height() * 0.75)))
                imagem_jogador = pygame.transform.smoothscale(imagem_jogador, tamanho)
        else:
            tamanho_original = imagem_jogador.get_size()
            if forma == "chamas":
                largura_desenho, altura_desenho = 118, 160
            else:
                largura_desenho, altura_desenho = 166, 132
            if abaixado:
                altura_desenho = int(altura_desenho * 0.68)
            imagem_jogador = pygame.transform.smoothscale(imagem_jogador, (largura_desenho, altura_desenho))

        if olhando_esquerda and not (forma == "bola" and rolando):
            imagem_jogador = pygame.transform.flip(imagem_jogador, True, False)

        if forma == "heroi":
            posicao_jogador = imagem_jogador.get_rect(midbottom=(jogador.centerx, CHAO - deslocamento_pulo))
        else:
            posicao_jogador = imagem_jogador.get_rect(midbottom=(jogador.centerx, CHAO - deslocamento_pulo))
        TELA.blit(imagem_jogador, posicao_jogador)

        for inimigo in inimigos:
            TELA.blit(INIMIGO_IMG, (int(inimigo[0]), int(inimigo[1])))

        TELA.blit(OMNITRIX_IMG, (20, 20))
        texto("Pontos: " + str(pontos), FONTE_MEDIA, BRANCO, 95, 30)
        nome_forma = "HERÓI" if forma == "heroi" else "CHAMAS" if forma == "chamas" else "BOLA DE CANHÃO"
        texto("Forma: " + nome_forma + " | G: escolher alien", FONTE_PEQUENA, VERDE_CLARO, 20, 590)
        texto("A/D: mover | SHIFT: correr | W: pular | S: agachar | clique: ataque",
              FONTE_PEQUENA, BRANCO, 20, 615)
        texto("Press Space to Pause Game.", FONTE_PEQUENA, BRANCO, 700, 665)

        if forma == "chamas" and aviso_ataque > 0:
            texto("Efeito de ataque ativado", FONTE_PEQUENA,
                  AMARELO, LARGURA//2, 555, True)

        if tempo_transformacao > 0:
            raio = int(75 + 18 * math.sin(tempo * 0.03))
            pygame.draw.circle(TELA, VERDE_CLARO, (jogador.centerx, CHAO - 70), raio, 5)

        if selecionando_alien:
            desenhar_menu_aliens()

        if pausa:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((0, 0, 0, 175))
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
        texto("FIM DE JOGO", FONTE_TITULO, VERMELHO, LARGURA//2, 150, True)
        texto(nome + " fez " + str(pontos) + " pontos.", FONTE_MEDIA, BRANCO,
              LARGURA//2, 250, True)
        texto("Maior competidor:", FONTE_MEDIA, VERDE, LARGURA//2, 350, True)
        texto(recorde_nome + " - " + str(recorde_pontos) + " pontos",
              FONTE_GRANDE, BRANCO, LARGURA//2, 405, True)
        texto("Data: " + recorde_data + "  Hora: " + recorde_hora,
              FONTE_PEQUENA, BRANCO, LARGURA//2, 465, True)
        texto("ENTER para jogar novamente", FONTE_PEQUENA, VERDE_CLARO,
              LARGURA//2, 550, True)
        texto("ESC para fechar", FONTE_PEQUENA, BRANCO,
              LARGURA//2, 590, True)
        pygame.display.flip()
        clock.tick(60)


def main():
    iniciar_musica()
    falar("Bem vindo ao Omnitrix Run.")
    while True:
        nome = tela_nome()
        tela_boas_vindas(nome)
        pontos = jogar(nome)
        tela_morte(nome, pontos)


main()
pygame.quit()
