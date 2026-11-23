import random

def criar_inimigo(largura_tela, y_fixo):
    """Cria um inimigo na mesma linha do chao do jogador."""
    x = largura_tela + random.randint(40, 220)
    velocidade = random.randint(4, 7)
    return [x, y_fixo, velocidade]

def mover_decoracao(x, y, velocidade_x, velocidade_y, largura, altura):
    """Move um objeto decorativo aleatoriamente, sem interagir com o jogador."""
    x += velocidade_x
    y += velocidade_y

    if x < 0 or x > largura - 40:
        velocidade_x *= -1
    if y < 70 or y > altura - 120:
        velocidade_y *= -1

    return x, y, velocidade_x, velocidade_y
