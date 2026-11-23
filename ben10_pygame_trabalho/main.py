import pygame
import random
import math
import os
from datetime import datetime
from Recursos.trabalho import criar_inimigo, mover_decoracao

pygame.init()

LARGURA = 1000
ALTURA = 700
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Omnitrix Run")
pygame.mixer.init()

BASE = os.path.join("bases")
FONTE_PATH = os.path.join(BASE, "fontes", "DejaVuSans-Bold.ttf")

def fonte(tamanho):
    if os.path.exists(FONTE_PATH):
        return pygame.font.Font(FONTE_PATH, tamanho)
    return pygame.font.SysFont("Arial", tamanho, bold=True)

FONTE_GRANDE = fonte(48)
FONTE_MEDIA = fonte(30)
FONTE_PEQUENA = fonte(18)
FONTE_TITULO = fonte(64)

def carregar_imagem(nome):
    return pygame.image.load(os.path.join(BASE, "imagens", nome)).convert_alpha()

FUNDO = pygame.image.load(os.path.join(BASE, "imagens", "fundo.png")).convert()
JOGADOR_IMG = carregar_imagem("jogador.png")
INIMIGO_IMG = carregar_imagem("inimigo.png")
PROJETIL_IMG = carregar_imagem("projetil.png")
OMNITRIX_IMG = carregar_imagem("icone_omnitrix.png")
DECORACAO_IMG = carregar_imagem("decoracao.png")

SOM_TIRO = pygame.mixer.Sound(os.path.join(BASE, "sons", "tiro.wav"))
SOM_PONTO = pygame.mixer.Sound(os.path.join(BASE, "sons", "ponto.wav"))
SOM_MORTE = pygame.mixer.Sound(os.path.join(BASE, "sons", "morte.wav"))

PRETO = (8, 10, 12)
BRANCO = (240, 245, 240)
VERDE = (70, 220, 110)
VERDE_CLARO = (130, 255, 150)
VERMELHO = (230, 80, 80)
AMARELO = (255, 220, 70)

clock = pygame.time.Clock()

def texto(texto, fonte_usada, cor, x, y, centro=False):
    imagem = fonte_usada.render(texto, True, cor)
    rect = imagem.get_rect()
    if centro:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    TELA.blit(imagem, rect)

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
    # O requisito da atividade pede o uso de pyttsx3.
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
        texto("OMNITRIX RUN", FONTE_TITULO, VERDE_CLARO, LARGURA//2, 170, True)
        texto("Digite seu nome:", FONTE_MEDIA, BRANCO, LARGURA//2, 290, True)

        pygame.draw.rect(TELA, (20, 45, 30), (300, 335, 400, 60), border_radius=10)
        pygame.draw.rect(TELA, VERDE, (300, 335, 400, 60), 2, border_radius=10)
        texto(nome + "_", FONTE_MEDIA, BRANCO, 320, 347)

        texto("ENTER para continuar", FONTE_PEQUENA, VERDE_CLARO, LARGURA//2, 450, True)
        texto("ESC para fechar", FONTE_PEQUENA, BRANCO, LARGURA//2, 490, True)

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

        texto("Mecânica:", FONTE_MEDIA, VERDE, 180, 250)
        texto("Mova o personagem apenas para os lados.", FONTE_PEQUENA, BRANCO, 180, 295)
        texto("Use Z para disparar e destruir inimigos.", FONTE_PEQUENA, BRANCO, 180, 325)
        texto("Evite os inimigos e faça a maior pontuação.", FONTE_PEQUENA, BRANCO, 180, 355)

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

def jogar(nome):
    jogador = pygame.Rect(120, 500, 70, 90)
    velocidade = 7
    inimigos = []
    projeteis = []
    pontos = 0
    tempo_inimigo = 0
    pausa = False
    acabou = False

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

                if evento.key == pygame.K_SPACE:
                    pausa = not pausa

                if not pausa and evento.key == pygame.K_z:
                    tiro = PROJETIL_IMG.get_rect()
                    tiro.x = jogador.right
                    tiro.centery = jogador.centery
                    projeteis.append(tiro)
                    SOM_TIRO.play()

        if not pausa:
            teclas = pygame.key.get_pressed()

            # O jogador se move SOMENTE no eixo X.
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                jogador.x -= velocidade
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                jogador.x += velocidade

            if jogador.left < 0:
                jogador.left = 0
            if jogador.right > LARGURA:
                jogador.right = LARGURA

            decor_x, decor_y, decor_vx, decor_vy = mover_decoracao(
                decor_x, decor_y, decor_vx, decor_vy, LARGURA, ALTURA
            )

            tempo_inimigo += dt
            if tempo_inimigo >= 900:
                inimigos.append(criar_inimigo(LARGURA, ALTURA))
                tempo_inimigo = 0

            for tiro in projeteis[:]:
                tiro.x += 12
                if tiro.left > LARGURA:
                    projeteis.remove(tiro)

            for inimigo in inimigos[:]:
                inimigo[0] -= inimigo[2]
                if inimigo[0] < -80:
                    inimigos.remove(inimigo)
                    continue

                inimigo_rect = INIMIGO_IMG.get_rect(topleft=(inimigo[0], inimigo[1]))

                if jogador.colliderect(inimigo_rect):
                    SOM_MORTE.play()
                    acabou = True

                for tiro in projeteis[:]:
                    if tiro.colliderect(inimigo_rect):
                        if tiro in projeteis:
                            projeteis.remove(tiro)
                        if inimigo in inimigos:
                            inimigos.remove(inimigo)
                        pontos += 10
                        SOM_PONTO.play()
                        break

        TELA.blit(FUNDO, (0, 0))
        desenhar_sol(tempo)

        TELA.blit(DECORACAO_IMG, (int(decor_x), int(decor_y)))
        TELA.blit(JOGADOR_IMG, jogador)

        for tiro in projeteis:
            TELA.blit(PROJETIL_IMG, tiro)

        for inimigo in inimigos:
            TELA.blit(INIMIGO_IMG, (int(inimigo[0]), int(inimigo[1])))

        TELA.blit(OMNITRIX_IMG, (20, 20))
        texto("Pontos: " + str(pontos), FONTE_MEDIA, BRANCO, 95, 30)
        texto("Z = atacar", FONTE_PEQUENA, VERDE_CLARO, 20, 615)
        texto("Press Space to Pause Game.", FONTE_PEQUENA, BRANCO, 700, 665)

        if pausa:
            pygame.draw.rect(TELA, (0, 0, 0), (0, 0, LARGURA, ALTURA), 0)
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
    falar("Bem vindo ao Omnitrix Run.")
    while True:
        nome = tela_nome()
        tela_boas_vindas(nome)
        pontos = jogar(nome)
        tela_morte(nome, pontos)

main()
pygame.quit()
