import random

def criar_inimigo(largura_tela, altura_tela):
    """Cria dados simples de um inimigo."""
    x = largura_tela + random.randint(0, 250)
    y = random.randint(480, altura_tela - 120)
    velocidade = random.randint(4, 7)
    return [x, y, velocidade]

def mover_decoracao(x, y, velocidade_x, velocidade_y, largura, altura):
    """Move um objeto decorativo de forma aleatoria, sem interacao com o jogador."""
    x += velocidade_x
    y += velocidade_y

    if x < 0 or x > largura - 40:
        velocidade_x *= -1
    if y < 70 or y > altura - 120:
        velocidade_y *= -1

    return x, y, velocidade_x, velocidade_y
