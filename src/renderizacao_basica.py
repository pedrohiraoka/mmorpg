import pygame, cPickle
from pygame.locals import * # Importa constantes como QUIT

# Inicialização do Pygame
pygame.init()

# === Carregamento de dados do mapa ===
# Carrega as matrizes do mapa de texturas e de objetos
tilemap = cPickle.load(file('data/tilemap.txt', 'r'))
objmap = cPickle.load(file('data/objmap.txt', 'r'))

running = True
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# === Constantes do mapa e tela ===
WIDTH, HEIGHT, TILE = 16, 11, 40

# Listas para armazenar as superfícies das imagens
tile, obj = [], []

# Carrega as imagens dos tiles e objetos (0 a 23)
for i in range(24):
    tile += [pygame.image.load(file('imagens/tile%s.png' % i))]
    obj += [pygame.image.load(file('imagens/obj%s.png' % i))]

# Loop principal do jogo com renderização
while running:
    # Tratamento básico do evento para fechar a janela
    for e in pygame.event.get():
        if e.type == QUIT:
            running = False

    # Controla o FPS
    clock.tick(7)

    # --- Renderização do cenário ---
    # 1. Desenha as texturas do chão (tiles)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Acessa o tipo de tile na matriz e desenha na posição correta
            screen.blit(tile[tilemap[y][x]], (x * TILE, y * TILE))

    # 2. Desenha os objetos (começando de índices negativos para objetos maiores)
    for y in range(-6, HEIGHT):
        for x in range(-4, WIDTH):
            if objmap[y][x] < 24: # Verifica se é um objeto válido (não é 255)
                screen.blit(obj[objmap[y][x]], (x * TILE, y * TILE))

    # Atualiza a tela inteira
    pygame.display.flip()