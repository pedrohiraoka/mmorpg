#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Servidor MMORPG 2D - Servidor centralizador multithreaded.

Este servidor gerencia o estado do mundo, valida movimentos e sincroniza
as ações entre todos os jogadores conectados via sockets TCP.

Funcionalidades:
- Escuta na porta 5000 em todas as interfaces (0.0.0.0)
- Cria uma thread dedicada para cada cliente conectado
- Mantém dicionário global de jogadores com posição e dados
- Valida movimentos dentro dos limites do mapa (0-499)
- Sincroniza adição/remoção de jogadores entre todos os clientes
- Responde a requisições de informação sobre posições do mapa

Uso: python servidor.py
"""

import socket
import threading
import pickle
import sys
from datetime import datetime

# Constantes do servidor
HOST = '0.0.0.0'  # Escutar em todas as interfaces
PORTA = 5000      # Porta de escuta
TAMANHO_MAPA = 500  # Mapa 500x500
POSICAO_INICIAL_X = 250  # Posição X inicial dos jogadores
POSICAO_INICIAL_Y = 250  # Posição Y inicial dos jogadores

# Tipos de eventos (devem corresponder aos do cliente)
EVENTO_GOTO = 24       # Movimentação
EVENTO_MESSAGE = 25    # Mensagem ao jogador
EVENTO_SETOBJECT = 26  # Criar/destruir objetos no mapa
EVENTO_SYSTEM = 27     # Mensagens do sistema
EVENTO_GETINFO = 28    # Requisitar informações de um ponto
EVENTO_MYID = 29       # Apresentação do jogador (sistema)

# Objeto vazio (usado para remover personagens do mapa)
OBJ_VAZIO = 255


class Jogador:
    """
    Classe que representa um jogador conectado ao servidor.
    
    Atributos:
        conexao (socket): Socket de conexão com o cliente
        id_personagem (int): ID visual do personagem (0-23)
        nome (str): Nome do jogador
        x (int): Posição X no mapa
        y (int): Posição Y no mapa
    """
    
    def __init__(self, conexao, id_personagem, nome, x, y):
        """
        Inicializa um novo jogador.
        
        Args:
            conexao (socket): Socket de conexão
            id_personagem (int): ID do personagem
            nome (str): Nome do jogador
            x (int): Posição X inicial
            y (int): Posição Y inicial
        """
        self.conexao = conexao
        self.id_personagem = id_personagem
        self.nome = nome
        self.x = x
        self.y = y
    
    def to_dict(self):
        """
        Converte o jogador para dicionário (para serialização).
        
        Returns:
            dict: Dicionário com dados do jogador
        """
        return {
            'id_personagem': self.id_personagem,
            'nome': self.nome,
            'x': self.x,
            'y': self.y
        }


class ServidorMMORPG:
    """
    Classe principal do servidor MMORPG.
    
    Gerencia conexões de clientes, estado do mundo e sincronização
    entre todos os jogadores conectados.
    """
    
    def __init__(self):
        """Inicializa o servidor com estruturas de dados vazias."""
        self.jogadores = {}  # Dict: endereco_cliente -> Jogador
        self.lock_jogadores = threading.Lock()  # Lock para acesso thread-safe
        self.socket_servidor = None
        self.contador_conexoes = 0
        print("=" * 60)
        print("SERVIDOR MMORPG 2D")
        print("=" * 60)
        print(f"Endereço: {HOST}:{PORTA}")
        print(f"Tamanho do mapa: {TAMANHO_MAPA}x{TAMANHO_MAPA}")
        print(f"Posição inicial: ({POSICAO_INICIAL_X}, {POSICAO_INICIAL_Y})")
        print("=" * 60)
    
    def criar_evento(self, tipo, **dados):
        """
        Cria um evento no formato serializável para envio aos clientes.
        
        Args:
            tipo (int): Tipo do evento (GOTO, MESSAGE, SETOBJECT, etc.)
            **dados: Dados adicionais do evento como argumentos nomeados
        
        Returns:
            str: String serializada do evento usando pickle
        """
        evento = {'type': tipo, 'data': dados}
        try:
            return pickle.dumps(evento)
        except Exception as e:
            print(f"[ERRO] Falha ao serializar evento: {e}")
            return None
    
    def enviar_para_todos(self, mensagem, exceto=None):
        """
        Envia uma mensagem para todos os jogadores conectados.
        
        Args:
            mensagem (bytes): Mensagem serializada para envio
            exceto (tuple, optional): Endereço do cliente a ser excluído do envio
        """
        with self.lock_jogadores:
            for endereco, jogador in list(self.jogadores.items()):
                if exceto and endereco == exceto:
                    continue
                try:
                    jogador.conexao.sendall(mensagem)
                except Exception as e:
                    print(f"[ERRO] Falha ao enviar para {endereco}: {e}")
    
    def adicionar_jogador(self, endereco, jogador):
        """
        Adiciona um jogador ao dicionário global e notifica todos.
        
        Args:
            endereco (tuple): Endereço (ip, porta) do cliente
            jogador (Jogador): Objeto Jogador a ser adicionado
        """
        with self.lock_jogadores:
            self.jogadores[endereco] = jogador
        
        # Enviar ao novo jogador todos os jogadores existentes
        for outro_endereco, outro_jogador in self.jogadores.items():
            if outro_endereco != endereco:
                evento = self.criar_evento(
                    EVENTO_SETOBJECT,
                    x=outro_jogador.x,
                    y=outro_jogador.y,
                    obj=outro_jogador.id_personagem
                )
                if evento:
                    try:
                        jogador.conexao.sendall(evento)
                    except:
                        pass
        
        # Notificar todos os outros sobre o novo jogador
        evento_novo = self.criar_evento(
            EVENTO_SETOBJECT,
            x=jogador.x,
            y=jogador.y,
            obj=jogador.id_personagem
        )
        if evento_novo:
            self.enviar_para_todos(evento_novo, exceto=endereco)
        
        # Enviar mensagem de boas-vindas
        evento_boas_vindas = self.criar_evento(
            EVENTO_MESSAGE,
            texto=f"Bem-vindo ao MMORPG, {jogador.nome}!"
        )
        if evento_boas_vindas:
            try:
                jogador.conexao.sendall(evento_boas_vindas)
            except:
                pass
        
        num_jogadores = len(self.jogadores)
        print(f"[{self._hora()}] Jogador '{jogador.nome}' conectado. Total: {num_jogadores}")
    
    def remover_jogador(self, endereco):
        """
        Remove um jogador do mapa e notifica todos os demais.
        
        Args:
            endereco (tuple): Endereço do cliente a ser removido
        """
        with self.lock_jogadores:
            if endereco not in self.jogadores:
                return
            
            jogador = self.jogadores.pop(endereco)
            
            # Remover personagem do mapa enviando OBJ_VAZIO para todos
            evento_remocao = self.criar_evento(
                EVENTO_SETOBJECT,
                x=jogador.x,
                y=jogador.y,
                obj=OBJ_VAZIO
            )
            if evento_remocao:
                self.enviar_para_todos(evento_remocao)
            
            print(f"[{self._hora()}] Jogador '{jogador.nome}' desconectado. Total: {len(self.jogadores)}")
    
    def processar_movimento(self, endereco, x_destino, y_destino):
        """
        Processa e valida um movimento de jogador.
        
        Valida se as coordenadas estão dentro dos limites do mapa,
        remove o personagem da posição antiga e adiciona na nova.
        
        Args:
            endereco (tuple): Endereço do cliente que solicitou o movimento
            x_destino (int): Coordenada X de destino
            y_destino (int): Coordenada Y de destino
        """
        with self.lock_jogadores:
            if endereco not in self.jogadores:
                return
            
            jogador = self.jogadores[endereco]
            
            # Validar limites do mapa (0 a 499)
            if not (0 <= x_destino < TAMANHO_MAPA and 0 <= y_destino < TAMANHO_MAPA):
                print(f"[{self._hora()}] Movimento inválido de {jogador.nome}: ({x_destino}, {y_destino})")
                return
            
            # Remover da posição antiga
            evento_remocao = self.criar_evento(
                EVENTO_SETOBJECT,
                x=jogador.x,
                y=jogador.y,
                obj=OBJ_VAZIO
            )
            if evento_remocao:
                self.enviar_para_todos(evento_remocao)
            
            # Atualizar posição
            jogador.x = x_destino
            jogador.y = y_destino
            
            # Adicionar na nova posição
            evento_adicao = self.criar_evento(
                EVENTO_SETOBJECT,
                x=jogador.x,
                y=jogador.y,
                obj=jogador.id_personagem
            )
            if evento_adicao:
                self.enviar_para_todos(evento_adicao)
            
            # Confirmar movimento ao próprio jogador
            evento_confirmacao = self.criar_evento(
                EVENTO_GOTO,
                x=x_destino,
                y=y_destino
            )
            if evento_confirmacao:
                try:
                    jogador.conexao.sendall(evento_confirmacao)
                except:
                    pass
    
    def processar_getinfo(self, endereco, x, y):
        """
        Processa uma requisição de informação sobre uma posição do mapa.
        
        Verifica se há algum jogador na posição especificada e responde.
        
        Args:
            endereco (tuple): Endereço do cliente que fez a requisição
            x (int): Coordenada X consultada
            y (int): Coordenada Y consultada
        """
        with self.lock_jogadores:
            jogador_encontrado = None
            
            # Procurar jogador na posição
            for jog in self.jogadores.values():
                if jog.x == x and jog.y == y:
                    jogador_encontrado = jog
                    break
            
            # Preparar mensagem de resposta
            if jogador_encontrado:
                texto = f"Posição ({x}, {y}): Jogador '{jogador_encontrado.nome}'"
            else:
                texto = f"Posição ({x}, {y}): Vazia"
            
            # Enviar resposta apenas ao cliente que perguntou
            evento_resposta = self.criar_evento(
                EVENTO_MESSAGE,
                texto=texto
            )
            if evento_resposta:
                try:
                    self.jogadores[endereco].conexao.sendall(evento_resposta)
                except:
                    pass
    
    def _hora(self):
        """
        Retorna timestamp formatado para logs.
        
        Returns:
            str: Timestamp no formato HH:MM:SS
        """
        return datetime.now().strftime("%H:%M:%S")
    
    def tratar_cliente(self, conexao, endereco):
        """
        Thread dedicada para tratar as mensagens de um cliente.
        
        Recebe eventos do cliente, interpreta e executa as ações
        apropriadas (movimento, info, apresentação, etc.).
        
        Args:
            conexao (socket): Socket de conexão com o cliente
            endereco (tuple): Endereço (ip, porta) do cliente
        """
        print(f"[{self._hora()}] Nova conexão de {endereco}")
        
        buffer = b""
        primeiro_evento = True
        
        try:
            while True:
                # Receber dados do cliente
                dados = conexao.recv(4096)
                
                if not dados:
                    # Cliente desconectou
                    break
                
                buffer += dados
                
                # Processar todos os eventos completos no buffer
                while len(buffer) > 0:
                    try:
                        # Tentar desserializar um evento
                        evento = pickle.loads(buffer)
                        
                        # Primeiro evento é sempre MYID (apresentação)
                        if primeiro_evento:
                            tipo = evento.get('type', EVENTO_MYID)
                            if tipo == EVENTO_MYID:
                                dados_evento = evento.get('data', {})
                                id_personagem = dados_evento.get('id', 14)
                                nome = dados_evento.get('name', 'Anonimo')
                                
                                # Criar jogador na posição inicial
                                jogador = Jogador(
                                    conexao,
                                    id_personagem,
                                    nome,
                                    POSICAO_INICIAL_X,
                                    POSICAO_INICIAL_Y
                                )
                                self.adicionar_jogador(endereco, jogador)
                                primeiro_evento = False
                            else:
                                print(f"[{self._hora()}] Primeiro evento inválido de {endereco}")
                                break
                        
                        else:
                            # Processar eventos normais
                            tipo = evento.get('type')
                            dados_evento = evento.get('data', {})
                            
                            if tipo == EVENTO_GOTO:
                                # Movimento
                                x = dados_evento.get('x', 0)
                                y = dados_evento.get('y', 0)
                                self.processar_movimento(endereco, x, y)
                            
                            elif tipo == EVENTO_GETINFO:
                                # Requisição de informação
                                x = dados_evento.get('x', 0)
                                y = dados_evento.get('y', 0)
                                self.processar_getinfo(endereco, x, y)
                            
                            else:
                                print(f"[{self._hora()}] Evento desconhecido tipo {tipo} de {endereco}")
                        
                        # Remover evento processado do buffer - encontrar fim do objeto pickle
                        # pickle.loads consome apenas parte do buffer, precisamos achar onde termina
                        try:
                            import io
                            stream = io.BytesIO(buffer)
                            # Pular o objeto que já foi lido
                            pickle.load(stream)
                            # Manter apenas o restante não lido
                            buffer = stream.read()
                        except:
                            buffer = b""
                        
                    except pickle.UnpicklingError:
                        # Buffer incompleto, aguardar mais dados
                        break
                    except EOFError:
                        # Buffer esvaziou durante leitura
                        buffer = b""
                        break
                    except Exception as e:
                        print(f"[{self._hora()}] Erro ao processar evento de {endereco}: {e}")
                        buffer = b""
                        break
        
        except Exception as e:
            print(f"[{self._hora()}] Erro na conexão com {endereco}: {e}")
        
        finally:
            # Limpeza na desconexão
            self.remover_jogador(endereco)
            try:
                conexao.close()
            except:
                pass
            print(f"[{self._hora()}] Conexão com {endereco} fechada")
    
    def iniciar(self):
        """
        Inicia o servidor e entra em loop de aceitação de conexões.
        
        Cria o socket servidor, configura para reutilizar endereço
        e fica escutando por conexões de clientes. Para cada nova
        conexão, cria uma thread dedicada.
        """
        # Criar socket
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # Vincular ao endereço e porta
            self.socket_servidor.bind((HOST, PORTA))
            self.socket_servidor.listen(10)  # Até 10 conexões pendentes
            
            print(f"[{self._hora()}] Servidor iniciado e escutando...")
            print("-" * 60)
            
            # Loop principal de aceitação
            while True:
                try:
                    conexao, endereco = self.socket_servidor.accept()
                    
                    # Criar thread para tratar o cliente
                    thread = threading.Thread(
                        target=self.tratar_cliente,
                        args=(conexao, endereco),
                        daemon=True
                    )
                    thread.start()
                    
                except KeyboardInterrupt:
                    print(f"\n[{self._hora()}] Interrupt recebido pelo teclado")
                    break
                except Exception as e:
                    print(f"[{self._hora()}] Erro ao aceitar conexão: {e}")
        
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao iniciar servidor: {e}")
            sys.exit(1)
        
        finally:
            # Fechamento gracioso
            if self.socket_servidor:
                self.socket_servidor.close()
            print(f"[{self._hora()}] Servidor encerrado")


def main():
    """Função principal que instancia e inicia o servidor."""
    servidor = ServidorMMORPG()
    servidor.iniciar()


if __name__ == "__main__":
    main()
