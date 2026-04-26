import pygame

# Inicializa todos os módulos do Pygame
pygame.init()

# Flag para controlar o loop principal
running = True

# Cria a janela do jogo com resolução 640x480 pixels
screen = pygame.display.set_mode((640, 480))

# Objeto Clock para controlar a taxa de quadros por segundo (FPS)
clock = pygame.time.Clock()

# Loop principal do jogo
while running:
    # Limita o loop a 7 quadros por segundo
    clock.tick(7)

# Nota do livro: Este código não tem tratamento para fechar a janela,
# então o programa irá "travar" e precisará ser fechado forçadamente.