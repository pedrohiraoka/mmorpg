import pygame, cPickle
from pygame.locals import *
from pygame.event import Event

# === Carregamento e Inicialização ===
tilemap = cPickle.load(file('data/tilemap.txt', 'r'))
objmap = cPickle.load(file('data/objmap.txt', 'r'))
running = True
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# === Eventos customizados do jogo ===
GOTO = 24
MESSAGE = 25
SETOBJECT = 26
SYSTEM = 27
GETINFO = 28

# === Configurações ===
WIDTH, HEIGHT, TILE = 16, 12, 40
MIDDLE = WIDTH/2 - 1 , HEIGHT/2 - 1 # Posição central do personagem na tela
tile, obj = [], []

# Carrega imagens
for i in range(24):
    tile += [pygame.image.load(file('imagens/tile%s.png' % i))]
    obj += [pygame.image.load(file('imagens/obj%s.png' % i))]

# === Estado do Jogo ===
# Deslocamento do mapa (canto superior esquerdo da tela)
slide_x = 0
slide_y = 0

# === Funções de Controle ===
def goto(x, y):
    """Move a visualização do mapa para centralizar na coordenada (x, y)."""
    global slide_x, slide_y
    slide_x = x - MIDDLE[0]
    slide_y = y - MIDDLE[1]
    pygame.display.set_caption("MMORPG Client - Pos: %2d, %2d" % (x, y))

def move((inc_x, inc_y)):
    """Cria um evento GOTO para mover o personagem se a velocidade não for zero."""
    if inc_x != 0 or inc_y != 0:
        # A nova posição é: deslocamento atual + incremento + centro da tela
        e = Event(GOTO, {'x': slide_x + inc_x + MIDDLE[0], 'y': slide_y + inc_y + MIDDLE[1]})
        pygame.event.post(e)

# Mapeamento das teclas para incrementos de velocidade
MOVES = {
    K_RIGHT: ( 1, 0),
    K_LEFT : (-1, 0),
    K_UP   : ( 0,-1),
    K_DOWN : ( 0, 1)
}

# Velocidade atual do personagem
moving = (0,0)

def handle():
    """Processa todos os eventos da fila do Pygame."""
    global running, moving
    for e in pygame.event.get():
        if e.type == QUIT:
            running = False
        elif e.type == KEYDOWN:
            # Se a tecla está no dicionário MOVES, adiciona à velocidade
            if e.key in MOVES.keys():
                moving = (moving[0] + MOVES[e.key][0], moving[1] + MOVES[e.key][1])
        elif e.type == KEYUP:
            # Se a tecla é solta, remove da velocidade
            if e.key in MOVES.keys():
                moving = (moving[0] - MOVES[e.key][0], moving[1] - MOVES[e.key][1])
        elif e.type == GOTO:
            goto(e.x, e.y)

# === Loop Principal ===
while running:
    clock.tick(7)
    handle() # Processa eventos do jogador
    move(moving) # Processa movimento pendente

    # Renderização do mapa (agora usando slide_x e slide_y)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            i, j = (slide_x + x, slide_y + y) # Coordenadas globais do mapa
            screen.blit(tile[tilemap[j][i]], (x * TILE, y * TILE))

    for y in range(-6, HEIGHT):
        for x in range(-4, WIDTH):
            i, j = (x + slide_x, slide_y + y)
            if objmap[j][i] < 24:
                screen.blit(obj[objmap[j][i]], (x * TILE, y * TILE))

    pygame.display.flip()