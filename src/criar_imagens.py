# criar_imagens.py
import pygame

pygame.init()

for i in range(24):
    # Cria superfície 40x40 com cor baseada no índice
    tile_surf = pygame.Surface((40, 40))
    # Cores diferentes para cada tile
    r = (i * 10) % 255
    g = (i * 20) % 255
    b = (i * 30) % 255
    tile_surf.fill((r, g, b))
    # Adiciona número para identificação
    font = pygame.font.SysFont("default", 12)
    text = font.render(str(i), True, (255, 255, 255))
    tile_surf.blit(text, (15, 15))
    
    pygame.image.save(tile_surf, f"imagens/tile{i}.png")
    
    # Objetos ligeiramente diferentes (mais escuros com borda)
    obj_surf = pygame.Surface((40, 40))
    obj_surf.fill((r//2, g//2, b//2))
    pygame.draw.rect(obj_surf, (255, 255, 255), (0, 0, 40, 40), 2)
    text = font.render(f"O{i}", True, (255, 255, 255))
    obj_surf.blit(text, (5, 15))
    
    pygame.image.save(obj_surf, f"imagens/obj{i}.png")

print("Imagens placeholder geradas!")