#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerador de mapas para o MMORPG 2D.

Este script gera dois arquivos de mapa:
- tilemap.txt: Matriz 500x500 de inteiros (0-23) representando texturas do terreno
- objmap.txt: Matriz 500x500 de inteiros (255=vazio, 0-23=objetos)

Os mapas são serializados usando pickle para eficiência.

Uso: python gerar_mapas.py
"""

import os
import random
import pickle

# Constantes
TAMANHO_MAPA = 500
NUM_TILES = 24  # IDs de 0 a 23
OBJ_VAZIO = 255  # Valor que representa célula vazia no objmap
PASTA_DATA = "data"


def gerar_tilemap():
    """
    Gera um mapa de texturas (tilemap) 500x500 com valores aleatórios.
    
    Returns:
        list: Matriz 2D 500x500 com inteiros de 0 a 23
    """
    print("Gerando tilemap (texturas do terreno)...")
    tilemap = []
    for y in range(TAMANHO_MAPA):
        linha = []
        for x in range(TAMANHO_MAPA):
            # Valor aleatório entre 0 e 23
            linha.append(random.randint(0, NUM_TILES - 1))
        tilemap.append(linha)
        
        # Progresso a cada 100 linhas
        if (y + 1) % 100 == 0:
            print(f"  {y + 1}/{TAMANHO_MAPA} linhas geradas")
    
    return tilemap


def gerar_objmap(tilemap):
    """
    Gera um mapa de objetos (objmap) 500x500 inicializado com 255 (vazio)
    e adiciona alguns objetos decorativos nas bordas.
    
    Args:
        tilemap (list): Mapa de texturas (usado como referência visual)
    
    Returns:
        list: Matriz 2D 500x500 com inteiros (255=vazio, 0-23=objetos)
    """
    print("Gerando objmap (objetos do cenário)...")
    objmap = []
    
    # Inicializar tudo como vazio (255)
    for y in range(TAMANHO_MAPA):
        linha = [OBJ_VAZIO] * TAMANHO_MAPA
        objmap.append(linha)
    
    # Adicionar objetos decorativos nas bordas do mapa
    print("  Adicionando objetos decorativos nas bordas...")
    
    # Bordas superior e inferior
    for x in range(0, TAMANHO_MAPA, 10):  # A cada 10 pixels
        # Borda superior
        objmap[0][x] = random.randint(0, 14)
        objmap[1][x] = random.randint(0, 14)
        # Borda inferior
        objmap[TAMANHO_MAPA - 1][x] = random.randint(0, 14)
        objmap[TAMANHO_MAPA - 2][x] = random.randint(0, 14)
    
    # Bordas esquerda e direita
    for y in range(0, TAMANHO_MAPA, 10):
        # Borda esquerda
        objmap[y][0] = random.randint(0, 14)
        objmap[y][1] = random.randint(0, 14)
        # Borda direita
        objmap[y][TAMANHO_MAPA - 1] = random.randint(0, 14)
        objmap[y][TAMANHO_MAPA - 2] = random.randint(0, 14)
    
    # Adicionar alguns objetos aleatórios espalhados pelo mapa
    print("  Espalhando objetos aleatórios pelo mapa...")
    num_objetos_aleatorios = 500
    for _ in range(num_objetos_aleatorios):
        x = random.randint(10, TAMANHO_MAPA - 11)
        y = random.randint(10, TAMANHO_MAPA - 11)
        obj_id = random.randint(0, 14)
        objmap[y][x] = obj_id
    
    print(f"  {num_objetos_aleatorios} objetos aleatórios adicionados")
    
    return objmap


def salvar_mapa(mapa, nome_arquivo, descricao):
    """
    Salva um mapa em arquivo usando pickle.
    
    Args:
        mapa (list): Matriz 2D do mapa
        nome_arquivo (str): Nome do arquivo na pasta data
        descricao (str): Descrição do mapa para logging
    """
    caminho_completo = os.path.join(PASTA_DATA, nome_arquivo)
    with open(caminho_completo, 'wb') as f:
        pickle.dump(mapa, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{descricao} salvo em: {caminho_completo}")


def main():
    """Função principal que gera e salva os mapas."""
    # Criar pasta data se não existir
    if not os.path.exists(PASTA_DATA):
        os.makedirs(PASTA_DATA)
        print(f"Pasta '{PASTA_DATA}' criada.")
    
    # Gerar tilemap
    tilemap = gerar_tilemap()
    
    # Gerar objmap baseado no tilemap
    objmap = gerar_objmap(tilemap)
    
    # Salvar ambos os mapas
    salvar_mapa(tilemap, "tilemap.txt", "Tilemap")
    salvar_mapa(objmap, "objmap.txt", "Objmap")
    
    print("\nMapas gerados com sucesso!")
    print(f"  Tilemap: {TAMANHO_MAPA}x{TAMANHO_MAPA} tiles")
    print(f"  Objmap: {TAMANHO_MAPA}x{TAMANHO_MAPA} objetos")


if __name__ == "__main__":
    main()
