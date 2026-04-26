import pygame, cPickle, thread, socket
from pygame.locals import *
pygame.init()
from pygame.event import Event

# === Eventos customizados ===
GOTO = 24       # Movimentar personagem
MESSAGE = 25    # Mensagem do servidor para o cliente
SETOBJECT = 26  # Criar/destruir objeto no mapa
SYSTEM = 27     # Mensagens do sistema
GETINFO = 28    # Requisitar informações de um ponto do mapa

# === Configurações de Rede ===
DESTINY = ("127.0.0.1", 5000)

# === Configurações da Tela ===
WIDTH, HEIGHT, TILE = 16, 11, 40
MIDDLE = WIDTH/2 - 1 , HEIGHT/2 - 1

# === Identidade do Jogador (Enviada ao servidor) ===
MYID = Event(SYSTEM, {'id': 15, 'name': 'anonimo'})

# === Carregamento dos Dados ===
tilemap = cPickle.load(file('data/tilemap.txt', 'r'))
objmap = cPickle.load(file('data/objmap.txt', 'r'))
running = True
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
tile, obj = [], []

# Carrega imagens
for i in range(24):
    tile += [pygame.image.load(file('imagens/tile%s.png' % i))]
    obj += [pygame.image.load(file('imagens/obj%s.png' % i))]

# === Função para texto na tela ===
font = pygame.font.SysFont("default", 16)
def settext(msg):
    """Renderiza uma mensagem de texto na barra inferior da tela."""
    global text
    text = pygame.Surface((640, 40))
    text.blit(font.render(msg, True, (255, 255, 255)), (5, 12))

# Inicializa o texto como vazio
settext("")

# === Estado do Jogo ===
slide_x = 0
slide_y = 0

def goto(x, y):
    """Move a visualização do mapa para a coordenada (x, y)."""
    global slide_x, slide_y
    slide_x = x - MIDDLE[0]
    slide_y = y - MIDDLE[1]
    pygame.display.set_caption("MMORPG Client - Pos: %2d, %2d" % (x, y))

def move((inc_x, inc_y)):
    """Envia um evento GOTO ao servidor para validar o movimento."""
    if inc_x != 0 or inc_y != 0:
        e = Event(GOTO, {'x': slide_x + inc_x + MIDDLE[0], 'y': slide_y + inc_y + MIDDLE[1]})
        send(str(e)) # Envia o movimento para o servidor

# === Funções de Rede ===
def listener():
    """Executada em uma thread, recebe dados do servidor continuamente."""
    while running:
        msg = conn.recv(999999)
        if msg != "":
            try:
                # Tenta interpretar a mensagem como uma lista de eventos Python
                for m in eval(msg):
                    pygame.event.post(m)
            except:
                # Se falhar, é uma mensagem de texto do servidor (debug)
                print "Servidor: ", msg

def send(event):
    """Envia um evento (como string) para o servidor."""
    conn.send(str(event))

# === Conexão com o Servidor ===
conn = socket.socket()
conn.connect(DESTINY)
thread.start_new_thread(listener, tuple()) # Inicia thread para ouvir o servidor
conn.send(str(MYID)) # Envia mensagem de apresentação

# Mapeamento de teclas
MOVES = {
    K_RIGHT: ( 1, 0),
    K_LEFT : (-1, 0),
    K_UP   : ( 0,-1),
    K_DOWN : ( 0, 1)
}

moving = (0,0)

def handle():
    """Processa todos os eventos da fila do Pygame."""
    global running, moving
    for e in pygame.event.get():
        if e.type == QUIT:
            running = False
        elif e.type == KEYDOWN:
            if e.key in MOVES.keys():
                moving = (moving[0] + MOVES[e.key][0], moving[1] + MOVES[e.key][1])
        elif e.type == KEYUP:
            if e.key in MOVES.keys():
                moving = (moving[0] - MOVES[e.key][0], moving[1] - MOVES[e.key][1])
        # Evento de clique do mouse para pedir informações ao servidor
        elif e.type == MOUSEBUTTONDOWN:
            pos = slide_x + e.pos[0]/TILE, slide_y + e.pos[1]/TILE
            send(Event(GETINFO, {'pos': pos}))
        # Eventos vindos do servidor
        elif e.type == GOTO:
            goto(e.x, e.y)
        elif e.type == MESSAGE:
            settext(e.msg)
        elif e.type == SYSTEM:
            print e.msg
        elif e.type == SETOBJECT:
            objmap[e.y][e.x] = e.obj

# === Loop Principal do Jogo ===
while running:
    clock.tick(7)
    handle() # Trata eventos
    move(moving) # Processa movimento

    # --- Renderização ---
    # Camada 1: Terreno (tiles)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            i, j = (slide_x + x, slide_y + y)
            screen.blit(tile[tilemap[j][i]], (x * TILE, y * TILE))

    # Camada 2: Objetos
    for y in range(-6, HEIGHT):
        for x in range(-4, WIDTH):
            i, j = (x + slide_x, slide_y + y)
            if objmap[j][i] < 24:
                screen.blit(obj[objmap[j][i]], (x * TILE, y * TILE))

    # Camada 3: Interface de texto (barra inferior)
    screen.blit(text, (0, 440))

    # Atualiza a tela
    pygame.display.flip()

# Encerra a conexão de forma limpa ao sair do loop
conn.send("bye bye")
conn.close()