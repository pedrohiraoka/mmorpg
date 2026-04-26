#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerador de imagens para o MMORPG 2D.

Este script gera 24 imagens PNG de 40x40 pixels para tiles e objetos.
Os tiles têm cores variadas baseadas no índice, enquanto os objetos
têm cores mais escuras com borda branca e texto identificador.

Uso: python criar_imagens.py
"""

import os
import pygame

# Constantes
NUM_IMAGENS = 24
TAMANHO = 40
PASTA_IMAGENS = "imagens"


def gerar_cor_tile(indice):
    """
    Gera uma cor RGB baseada no índice do tile.
    
    Args:
        indice (int): Índice do tile (0-23)
    
    Returns:
        tuple: Cor RGB (r, g, b)
    """
    # Variação de cores usando seno para criar gradiente suave
    r = int(100 + 155 * ((indice * 15) % 256) / 256.0)
    g = int(100 + 155 * ((indice * 30) % 256) / 256.0)
    b = int(100 + 155 * ((indice * 45) % 256) / 256.0)
    return (r, g, b)


def gerar_cor_objeto(indice):
    """
    Gera uma cor RGB mais escura para objetos baseada no índice.
    
    Args:
        indice (int): Índice do objeto (0-23)
    
    Returns:
        tuple: Cor RGB (r, g, b) mais escura
    """
    r, g, b = gerar_cor_tile(indice)
    # Escurecer a cor
    r = max(0, r - 50)
    g = max(0, g - 50)
    b = max(0, b - 50)
    return (r, g, b)


def desenhar_borda_branca(surface, espessura=2):
    """
    Desenha uma borda branca ao redor da superfície.
    
    Args:
        surface (pygame.Surface): Superfície para desenhar
        espessura (int): Espessura da borda em pixels
    """
    rect = surface.get_rect()
    pygame.draw.rect(surface, (255, 255, 255), rect, espessura)


def criar_tile(indice):
    """
    Cria uma imagem de tile 40x40 com cor baseada no índice e número centralizado.
    
    Args:
        indice (int): Índice do tile (0-23)
    
    Returns:
        pygame.Surface: Superfície contendo o tile renderizado
    """
    surface = pygame.Surface((TAMANHO, TAMANHO))
    cor = gerar_cor_tile(indice)
    surface.fill(cor)
    
    # Renderizar número do tile
    fonte = pygame.font.Font(None, 28)
    texto = fonte.render(str(indice), True, (255, 255, 255))
    texto_rect = texto.get_rect(center=(TAMANHO // 2, TAMANHO // 2))
    surface.blit(texto, texto_rect)
    
    return surface


def criar_objeto(indice):
    """
    Cria uma imagem de objeto 40x40 com cor escura, borda branca e texto 'O<n>'.
    
    Args:
        indice (int): Índice do objeto (0-23)
    
    Returns:
        pygame.Surface: Superfície contendo o objeto renderizado
    """
    surface = pygame.Surface((TAMANHO, TAMANHO))
    cor = gerar_cor_objeto(indice)
    surface.fill(cor)
    
    # Desenhar borda branca
    desenhar_borda_branca(surface, 2)
    
    # Renderizar texto do objeto
    fonte = pygame.font.Font(None, 28)
    texto = fonte.render(f"O{indice}", True, (255, 255, 255))
    texto_rect = texto.get_rect(center=(TAMANHO // 2, TAMANHO // 2))
    surface.blit(texto, texto_rect)
    
    return surface


def main():
    """Função principal que gera todas as imagens."""
    # Inicializar Pygame
    pygame.init()
    
    # Criar pasta de imagens se não existir
    if not os.path.exists(PASTA_IMAGENS):
        os.makedirs(PASTA_IMAGENS)
        print(f"Pasta '{PASTA_IMAGENS}' criada.")
    
    print("Gerando imagens de tiles...")
    for i in range(NUM_IMAGENS):
        tile = criar_tile(i)
        caminho = os.path.join(PASTA_IMAGENS, f"tile{i}.png")
        pygame.image.save(tile, caminho)
        print(f"  Criado: {caminho}")
    
    print("\nGerando imagens de objetos...")
    for i in range(NUM_IMAGENS):
        obj = criar_objeto(i)
        caminho = os.path.join(PASTA_IMAGENS, f"obj{i}.png")
        pygame.image.save(obj, caminho)
        print(f"  Criado: {caminho}")
    
    print(f"\nTotal de {NUM_IMAGENS * 2} imagens geradas na pasta '{PASTA_IMAGENS}'.")
    pygame.quit()


if __name__ == "__main__":
    main()
