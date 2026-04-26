#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cliente MMORPG 2D - Interface gráfica com Pygame.

Este cliente se conecta ao servidor MMORPG, renderiza o mapa, captura
eventos do jogador e os envia para validação do servidor.

Funcionalidades:
- Renderização de mapa 500x500 com tiles e objetos
- Sistema de câmera que segue o jogador
- Movimentação com teclas direcionais (incluindo diagonal)
- Clique para obter informações sobre posições do mapa
- Visualização de outros jogadores conectados
- Exibição de mensagens na parte inferior da tela

Uso: python cliente.py
"""

import pygame
from pygame.locals import *
import socket
import threading
import pickle
import sys
import os

# Constantes de configuração da janela
LARGURA_TELA = 640
ALTURA_TELA = 480
TAMANHO_TILE = 40
COLUNAS_VISIVEIS = 16  # 640 / 40
LINHAS_VISIVEIS = 11   # (480 - 40) / 40 = 11 linhas visíveis + 1 linha de texto
ALTURA_TEXTO = 40      # Área inferior para mensagens

# Constantes de tipos de eventos
EVENTO_GOTO = 24       # Movimentação
EVENTO_MESSAGE = 25    # Mensagem ao jogador
EVENTO_SETOBJECT = 26  # Criar/destruir objetos no mapa
EVENTO_SYSTEM = 27     # Mensagens do sistema
EVENTO_GETINFO = 28    # Requisitar informações de um ponto
EVENTO_MYID = 29       # Apresentação do jogador

# Configurações do servidor
SERVIDOR_HOST = '127.0.0.1'  # localhost
SERVIDOR_PORTA = 5000

# Tamanho do mapa
TAMANHO_MAPA = 500

# Objeto vazio
OBJ_VAZIO = 255

# Posição inicial padrão
POSICAO_INICIAL_X = 250
POSICAO_INICIAL_Y = 250

# Dicionário de movimentos (tecla -> delta x, delta y)
MOVES = {
    K_RIGHT: (1, 0),
    K_LEFT: (-1, 0),
    K_UP: (0, -1),
    K_DOWN: (0, 1)
}


class ClienteMMORPG:
    """
    Classe principal do cliente MMORPG.
    
    Gerencia conexão com servidor, renderização gráfica, entrada do usuário
    e processamento de eventos da rede.
    """
    
    def __init__(self):
        """Inicializa o cliente com todas as estruturas de dados."""
        # Conexão com servidor
        self.socket_servidor = None
        self.conectado = False
        
        # Estado do jogo
        self.slide_x = 0  # Posição X da câmera (canto superior esquerdo)
        self.slide_y = 0  # Posição Y da câmera
        self.moving = (0, 0)  # Velocidade atual (vx, vy)
        self.mensagem_exibicao = ""  # Mensagem na área inferior
        
        # Dados do jogador local
        self.jogador_id = 14  # ID do personagem (14-19)
        self.jogador_nome = "Jogador"
        
        # Mapas
        self.tilemap = []  # Matriz 500x500 de texturas
        self.objmap = []   # Matriz 500x500 de objetos
        
        # Sprites
        self.tiles = []    # Lista de imagens dos tiles (0-23)
        self.objetos = []  # Lista de imagens dos objetos (0-23)
        
        # Thread listener
        self.thread_listener = None
        self.running_listener = True
        
        print("=" * 60)
        print("CLIENTE MMORPG 2D")
        print("=" * 60)
    
    def carregar_imagens(self):
        """
        Carrega todas as imagens de tiles e objetos da pasta 'imagens'.
        
        Procura por tile0.png até tile23.png e obj0.png até obj23.png.
        Em caso de falha, cria imagens placeholder coloridas.
        """
        print("Carregando imagens...")
        
        pasta_imagens = "imagens"
        
        # Criar superfície temporária para conversão (não requer display)
        superficie_temp = pygame.Surface((TAMANHO_TILE, TAMANHO_TILE))
        
        # Carregar tiles
        self.tiles = []
        for i in range(24):
            caminho = os.path.join(pasta_imagens, f"tile{i}.png")
            try:
                img = pygame.image.load(caminho)
                # Usar convert() apenas se display estiver disponível
                try:
                    img = img.convert()
                except pygame.error:
                    pass  # Sem display, usar imagem como está
                self.tiles.append(img)
            except FileNotFoundError:
                print(f"  Aviso: {caminho} não encontrado, criando placeholder")
                # Criar placeholder
                img = pygame.Surface((TAMANHO_TILE, TAMANHO_TILE))
                cor = (100 + i * 5, 100 + i * 3, 100 + i * 7)
                img.fill(cor)
                self.tiles.append(img)
        
        # Carregar objetos
        self.objetos = []
        for i in range(24):
            caminho = os.path.join(pasta_imagens, f"obj{i}.png")
            try:
                img = pygame.image.load(caminho)
                # Usar convert_alpha() apenas se display estiver disponível
                try:
                    img = img.convert_alpha()
                except pygame.error:
                    pass  # Sem display, usar imagem como está
                self.objetos.append(img)
            except FileNotFoundError:
                print(f"  Aviso: {caminho} não encontrado, criando placeholder")
                # Criar placeholder
                img = pygame.Surface((TAMANHO_TILE, TAMANHO_TILE))
                cor = (50 + i * 5, 50 + i * 3, 50 + i * 7)
                img.fill(cor)
                pygame.draw.rect(img, (255, 255, 255), img.get_rect(), 2)
                self.objetos.append(img)
        
        print(f"  {len(self.tiles)} tiles carregados")
        print(f"  {len(self.objetos)} objetos carregados")
    
    def carregar_mapas(self):
        """
        Carrega os mapas tilemap.txt e objmap.txt da pasta 'data'.
        
        Usa pickle para desserializar as matrizes 500x500.
        """
        print("Carregando mapas...")
        
        pasta_data = "data"
        
        # Carregar tilemap
        caminho_tilemap = os.path.join(pasta_data, "tilemap.txt")
        try:
            with open(caminho_tilemap, 'rb') as f:
                self.tilemap = pickle.load(f)
            print(f"  Tilemap carregado: {len(self.tilemap)}x{len(self.tilemap[0]) if self.tilemap else 0}")
        except FileNotFoundError:
            print(f"  ERRO: {caminho_tilemap} não encontrado!")
            self._criar_mapa_placeholder(self.tilemap, 0)
        except Exception as e:
            print(f"  ERRO ao carregar tilemap: {e}")
            self._criar_mapa_placeholder(self.tilemap, 0)
        
        # Carregar objmap
        caminho_objmap = os.path.join(pasta_data, "objmap.txt")
        try:
            with open(caminho_objmap, 'rb') as f:
                self.objmap = pickle.load(f)
            print(f"  Objmap carregado: {len(self.objmap)}x{len(self.objmap[0]) if self.objmap else 0}")
        except FileNotFoundError:
            print(f"  ERRO: {caminho_objmap} não encontrado!")
            self._criar_mapa_placeholder(self.objmap, OBJ_VAZIO)
        except Exception as e:
            print(f"  ERRO ao carregar objmap: {e}")
            self._criar_mapa_placeholder(self.objmap, OBJ_VAZIO)
    
    def _criar_mapa_placeholder(self, mapa, valor_padrao):
        """
        Cria um mapa placeholder 500x500 com valor padrão.
        
        Args:
            mapa (list): Lista a ser preenchida (será modificada in-place)
            valor_padrao (int): Valor para preencher todas as células
        """
        mapa.clear()
        for _ in range(TAMANHO_MAPA):
            mapa.append([valor_padrao] * TAMANHO_MAPA)
    
    def conectar_servidor(self):
        """
        Estabelece conexão com o servidor MMORPG.
        
        Tenta conectar em localhost:5000. Se falhar, exibe erro e termina.
        """
        print(f"Tentando conectar ao servidor {SERVIDOR_HOST}:{SERVIDOR_PORTA}...")
        
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.connect((SERVIDOR_HOST, SERVIDOR_PORTA))
            self.conectado = True
            print("Conectado ao servidor!")
        except ConnectionRefusedError:
            print(f"ERRO: Servidor recusou conexão em {SERVIDOR_HOST}:{SERVIDOR_PORTA}")
            print("Verifique se o servidor está rodando (python servidor.py)")
            return False
        except Exception as e:
            print(f"ERRO: Falha ao conectar: {e}")
            return False
        
        return True
    
    def enviar_evento(self, tipo, **dados):
        """
        Envia um evento para o servidor.
        
        Serializa o evento usando pickle e envia pelo socket.
        
        Args:
            tipo (int): Tipo do evento (GOTO, GETINFO, MYID, etc.)
            **dados: Dados adicionais como argumentos nomeados
        """
        if not self.conectado or not self.socket_servidor:
            return
        
        evento = {'type': tipo, 'data': dados}
        try:
            dados_serializados = pickle.dumps(evento)
            self.socket_servidor.sendall(dados_serializados)
        except Exception as e:
            print(f"ERRO ao enviar evento: {e}")
            self.conectado = False
    
    def listener(self):
        """
        Thread que escuta mensagens do servidor continuamente.
        
        Recebe dados do socket, desserializa eventos usando pickle
        e os adiciona à fila de eventos do Pygame para processamento.
        """
        buffer = b""
        
        while self.running_listener and self.conectado:
            try:
                # Receber dados do servidor
                dados = self.socket_servidor.recv(4096)
                
                if not dados:
                    # Servidor fechou conexão
                    print("Servidor fechou conexão")
                    self.conectado = False
                    break
                
                buffer += dados
                
                # Processar todos os eventos completos no buffer
                while True:
                    try:
                        evento = pickle.loads(buffer)
                        
                        # Converter para evento Pygame customizado
                        tipo_evento = evento.get('type', EVENTO_SYSTEM)
                        dados_evento = evento.get('data', {})
                        
                        # Criar evento Pygame customizado
                        pygame_event = pygame.event.Event(USEREVENT + tipo_evento - 24, dados_evento)
                        pygame.event.post(pygame_event)
                        
                        # Remover evento processado do buffer
                        buffer = b""
                        
                    except pickle.UnpicklingError:
                        # Buffer incompleto, aguardar mais dados
                        break
                    except Exception as e:
                        print(f"ERRO ao processar evento do servidor: {e}")
                        buffer = b""
                        break
            
            except Exception as e:
                if self.running_listener:
                    print(f"ERRO no listener: {e}")
                self.conectado = False
                break
        
        print("Listener encerrado")
    
    def goto(self, x, y):
        """
        Centraliza a câmera na posição especificada.
        
        Atualiza slide_x e slide_y para que a posição (x, y) fique
        centralizada na tela. Também atualiza o título da janela.
        
        Args:
            x (int): Coordenada X global para centralizar
            y (int): Coordenada Y global para centralizar
        """
        # Calcular posição da câmera para centralizar o jogador
        meio_x = COLUNAS_VISIVEIS // 2
        meio_y = LINHAS_VISIVEIS // 2
        
        self.slide_x = x - meio_x
        self.slide_y = y - meio_y
        
        # Manter câmera dentro dos limites do mapa
        self.slide_x = max(0, min(self.slide_x, TAMANHO_MAPA - COLUNAS_VISIVEIS))
        self.slide_y = max(0, min(self.slide_y, TAMANHO_MAPA - LINHAS_VISIVEIS))
        
        # Atualizar título da janela com posição atual
        pos_jogador_x = self.slide_x + meio_x
        pos_jogador_y = self.slide_y + meio_y
        pygame.display.set_caption(f"MMORPG Client - Posição: ({pos_jogador_x}, {pos_jogador_y})")
    
    def aplicar_movimento(self):
        """
        Aplica o movimento atual e envia nova posição ao servidor.
        
        Verifica se há movimento pendente (moving != (0, 0)), calcula
        a nova posição e envia evento GOTO ao servidor.
        """
        if self.moving == (0, 0):
            return
        
        # Calcular nova posição baseada no movimento atual
        # A posição atual do jogador é sempre centralizada
        meio_x = COLUNAS_VISIVEIS // 2
        meio_y = LINHAS_VISIVEIS // 2
        pos_atual_x = self.slide_x + meio_x
        pos_atual_y = self.slide_y + meio_y
        
        nova_x = pos_atual_x + self.moving[0]
        nova_y = pos_atual_y + self.moving[1]
        
        # Enviar movimento ao servidor (não move localmente)
        self.enviar_evento(EVENTO_GOTO, x=nova_x, y=nova_y)
    
    def renderizar(self, tela):
        """
        Renderiza o estado atual do jogo na tela.
        
        Renderiza em três camadas:
        1. Tiles do terreno (base)
        2. Objetos e personagens
        3. Área de texto inferior
        
        Args:
            tela (pygame.Surface): Superfície da tela para renderização
        """
        # Limpar tela com cor preta
        tela.fill((0, 0, 0))
        
        # Camada 1: Renderizar tiles do terreno
        for y in range(LINHAS_VISIVEIS):
            for x in range(COLUNAS_VISIVEIS):
                # Coordenadas globais no mapa
                gx = self.slide_x + x
                gy = self.slide_y + y
                
                # Verificar limites do mapa
                if 0 <= gx < TAMANHO_MAPA and 0 <= gy < TAMANHO_MAPA:
                    # Obter ID do tile
                    tile_id = self.tilemap[gy][gx] if self.tilemap else 0
                    tile_id = min(max(tile_id, 0), 23)  # Garantir intervalo válido
                    
                    # Desenhar tile
                    if 0 <= tile_id < len(self.tiles):
                        tela.blit(self.tiles[tile_id], (x * TAMANHO_TILE, y * TAMANHO_TILE))
        
        # Camada 2: Renderizar objetos (área estendida para objetos grandes)
        offset_x = -6
        offset_y = -4
        for y in range(LINHAS_VISIVEIS + abs(offset_y) * 2):
            for x in range(COLUNAS_VISIVEIS + abs(offset_x) * 2):
                # Coordenadas globais
                gx = self.slide_x + x + offset_x
                gy = self.slide_y + y + offset_y
                
                # Verificar limites do mapa
                if 0 <= gx < TAMANHO_MAPA and 0 <= gy < TAMANHO_MAPA:
                    # Obter ID do objeto
                    obj_id = self.objmap[gy][gx] if self.objmap else OBJ_VAZIO
                    
                    # Desenhar apenas objetos válidos (0-23)
                    if 0 <= obj_id < 24:
                        px = (x + offset_x) * TAMANHO_TILE
                        py = (y + offset_y) * TAMANHO_TILE
                        
                        if 0 <= obj_id < len(self.objetos):
                            tela.blit(self.objetos[obj_id], (px, py))
        
        # Camada 3: Área de texto inferior
        superficie_texto = pygame.Surface((LARGURA_TELA, ALTURA_TEXTO))
        superficie_texto.fill((30, 30, 30))
        tela.blit(superficie_texto, (0, ALTURA_TELA - ALTURA_TEXTO))
        
        # Renderizar mensagem
        if self.mensagem_exibicao:
            fonte = pygame.font.Font(None, 24)
            texto = fonte.render(self.mensagem_exibicao, True, (255, 255, 255))
            tela.blit(texto, (10, ALTURA_TELA - ALTURA_TEXTO + 10))
        
        # Mostrar FPS
        fonte_fps = pygame.font.Font(None, 20)
        fps_texto = fonte_fps.render(f"FPS: {int(pygame.time.Clock().get_fps())}", True, (200, 200, 200))
        tela.blit(fps_texto, (LARGURA_TELA - 80, 10))
    
    def executar(self):
        """
        Loop principal do cliente.
        
        Inicializa Pygame, conecta ao servidor, inicia thread listener
        e entra no loop de eventos principal. Processa entrada do usuário,
        renderiza o jogo e comunica com o servidor.
        """
        # Inicializar Pygame
        pygame.init()
        pygame.display.set_caption("MMORPG Client")
        
        # Criar janela
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        clock = pygame.time.Clock()
        
        # Carregar recursos
        self.carregar_imagens()
        self.carregar_mapas()
        
        # Conectar ao servidor
        if not self.conectar_servidor():
            pygame.quit()
            return
        
        # Enviar evento de apresentação (MYID)
        self.enviar_evento(EVENTO_MYID, id=self.jogador_id, name=self.jogador_nome)
        
        # Iniciar thread listener
        self.thread_listener = threading.Thread(target=self.listener, daemon=True)
        self.thread_listener.start()
        
        # Centralizar câmera na posição inicial
        self.goto(POSICAO_INICIAL_X, POSICAO_INICIAL_Y)
        
        print("-" * 60)
        print("Controles:")
        print("  Setas direcionais: Mover")
        print("  Clique do mouse: Obter informação da posição")
        print("  ESC ou fechar janela: Sair")
        print("-" * 60)
        
        # Loop principal
        rodando = True
        while rodando:
            # Processar eventos
            for evento in pygame.event.get():
                if evento.type == QUIT:
                    rodando = False
                
                elif evento.type == KEYDOWN:
                    if evento.key == K_ESCAPE:
                        rodando = False
                    elif evento.key in MOVES:
                        # Adicionar direção ao movimento
                        dx, dy = MOVES[evento.key]
                        self.moving = (self.moving[0] + dx, self.moving[1] + dy)
                
                elif evento.type == KEYUP:
                    if evento.key in MOVES:
                        # Remover direção do movimento
                        dx, dy = MOVES[evento.key]
                        self.moving = (self.moving[0] - dx, self.moving[1] - dy)
                
                elif evento.type == MOUSEBUTTONDOWN:
                    # Clique para obter informação
                    if evento.button == 1:  # Botão esquerdo
                        # Converter posição do clique para coordenadas globais
                        mouse_x, mouse_y = evento.pos
                        tile_x = mouse_x // TAMANHO_TILE
                        tile_y = mouse_y // TAMANHO_TILE
                        
                        # Coordenadas globais no mapa
                        gx = self.slide_x + tile_x
                        gy = self.slide_y + tile_y
                        
                        # Enviar requisição de informação
                        self.enviar_evento(EVENTO_GETINFO, x=gx, y=gy)
                
                elif evento.type == USEREVENT + (EVENTO_GOTO - 24):
                    # Evento GOTO do servidor - mover câmera
                    x = evento.data.get('x', 0)
                    y = evento.data.get('y', 0)
                    self.goto(x, y)
                
                elif evento.type == USEREVENT + (EVENTO_MESSAGE - 24):
                    # Mensagem do servidor - exibir na tela
                    texto = evento.data.get('texto', '')
                    self.mensagem_exibicao = texto
                
                elif evento.type == USEREVENT + (EVENTO_SYSTEM - 24):
                    # Mensagem do sistema - imprimir no console
                    texto = evento.data.get('texto', '')
                    print(f"[SISTEMA] {texto}")
                
                elif evento.type == USEREVENT + (EVENTO_SETOBJECT - 24):
                    # Atualizar objeto no mapa
                    x = evento.data.get('x', 0)
                    y = evento.data.get('y', 0)
                    obj = evento.data.get('obj', OBJ_VAZIO)
                    
                    if 0 <= x < TAMANHO_MAPA and 0 <= y < TAMANHO_MAPA:
                        self.objmap[y][x] = obj
            
            # Aplicar movimento
            self.aplicar_movimento()
            
            # Renderizar
            self.renderizar(tela)
            
            # Atualizar display
            pygame.display.flip()
            
            # Limitar a 7 FPS conforme especificação
            clock.tick(7)
        
        # Encerramento
        print("Encerrando cliente...")
        self.running_listener = False
        
        # Enviar despedida ao servidor
        if self.conectado and self.socket_servidor:
            try:
                self.socket_servidor.sendall(pickle.dumps({'type': EVENTO_SYSTEM, 'data': {'texto': 'bye bye'}}))
            except:
                pass
            
            self.socket_servidor.close()
        
        pygame.quit()
        print("Cliente encerrado.")


def main():
    """Função principal que instancia e executa o cliente."""
    cliente = ClienteMMORPG()
    cliente.executar()


if __name__ == "__main__":
    main()
