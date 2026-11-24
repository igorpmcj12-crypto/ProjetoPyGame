import random


def criar_inimigo(largura_tela, y_fixo, velocidade=2.0):
    """Cria um ratinho na trilha, perto do chefe e na altura do jogador."""
    x = largura_tela - random.randint(150, 260)
    return [x, y_fixo, velocidade]


def mover_decoracao(x, y, velocidade_x, velocidade_y, largura, altura):
    """Move um detalhe decorativo pelo cenario, sem interagir com o jogador."""
    x += velocidade_x
    y += velocidade_y

    if x < 0 or x > largura - 40:
        velocidade_x *= -1
    if y < 70 or y > altura - 170:
        velocidade_y *= -1

    return x, y, velocidade_x, velocidade_y
