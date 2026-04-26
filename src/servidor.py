# servidor.py
import socket
import thread
import sys

# Configuração do servidor
HOST = ''  # Aceita conexões de qualquer interface
PORT = 5000

# Mapa de jogadores conectados: { conexão: (id_personagem, nome, pos_x, pos_y) }
jogadores = {}

def broadcast(evento_str, origem=None):
    """Envia uma mensagem para todos os clientes, exceto o de origem (se especificado)."""
    for conn in jogadores.keys():
        if conn != origem:
            try:
                conn.send(evento_str)
            except:
                pass

def tratar_cliente(conn, addr):
    """Thread para cada cliente conectado."""
    global jogadores
    
    # Aguarda primeira mensagem (apresentação do jogador)
    msg = conn.recv(1024)
    try:
        dados = eval(msg)
        player_id = dados.id
        player_name = dados.name
        # Posição inicial aleatória dentro do mapa 500x500
        start_x, start_y = 250, 250
        
        jogadores[conn] = (player_id, player_name, start_x, start_y)
        print(f"Jogador {player_name} (ID:{player_id}) conectado de {addr}")
        
        # Cria evento SETOBJECT para adicionar personagem no mapa de todos
        evento_novo_jogador = f"[Event(26, {{'x': {start_x}, 'y': {start_y}, 'obj': {player_id}}})]"
        
        # Envia todos os jogadores existentes para o novo cliente
        for conn_existente, (pid, pnome, px, py) in jogadores.items():
            evento_existente = f"[Event(26, {{'x': {px}, 'y': {py}, 'obj': {pid}}})]"
            conn.send(evento_existente)
        
        # Avisa a todos sobre o novo jogador
        broadcast(evento_novo_jogador, conn)
        
        # Envia mensagem de boas-vindas
        boas_vindas = f"[Event(25, {{'msg': 'Bem-vindo ao MMORPG, {player_name}!'}})]"
        conn.send(boas_vindas)
        
    except Exception as e:
        print(f"Erro ao processar apresentação: {e}")
        conn.close()
        return
    
    # Loop de recebimento de mensagens do cliente
    while True:
        try:
            msg = conn.recv(999999)
            if not msg or msg == "bye bye":
                break
            
            # Processa evento recebido
            evento = eval(msg)
            
            if evento.type == 24:  # GOTO - Movimento
                nova_x, nova_y = evento.x, evento.y
                
                # Validação simples: dentro do mapa (0-499)?
                if 0 <= nova_x < 500 and 0 <= nova_y < 500:
                    old_id, nome, old_x, old_y = jogadores[conn]
                    
                    # Remove personagem da posição antiga
                    evento_remover = f"[Event(26, {{'x': {old_x}, 'y': {old_y}, 'obj': 255}})]"
                    broadcast(evento_remover)
                    
                    # Atualiza posição
                    jogadores[conn] = (old_id, nome, nova_x, nova_y)
                    
                    # Adiciona personagem na nova posição
                    evento_adicionar = f"[Event(26, {{'x': {nova_x}, 'y': {nova_y}, 'obj': {old_id}}})]"
                    broadcast(evento_adicionar)
                    
                    # Confirma movimento para quem andou
                    confirmacao = f"[Event(24, {{'x': {nova_x}, 'y': {nova_y}}})]"
                    conn.send(confirmacao)
            
            elif evento.type == 28:  # GETINFO - Clique no mapa
                pos = evento.pos
                # Verifica se há algum jogador na posição clicada
                jogador_encontrado = None
                for conn_j, (pid, pnome, px, py) in jogadores.items():
                    if (px, py) == pos:
                        jogador_encontrado = (pid, pnome)
                        break
                
                if jogador_encontrado:
                    resposta = f"[Event(25, {{'msg': 'Jogador {jogador_encontrado[1]} (ID:{jogador_encontrado[0]}) nesta posicao'}})]"
                else:
                    resposta = f"[Event(25, {{'msg': 'Posicao ({pos[0]}, {pos[1]}) vazia'}})]"
                
                conn.send(resposta)
                
        except Exception as e:
            print(f"Erro com cliente {addr}: {e}")
            break
    
    # Desconexão do jogador
    if conn in jogadores:
        pid, nome, px, py = jogadores[conn]
        evento_remover = f"[Event(26, {{'x': {px}, 'y': {py}, 'obj': 255}})]"
        broadcast(evento_remover)
        del jogadores[conn]
        print(f"Jogador {nome} desconectado")
    
    conn.close()


# Inicialização do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Servidor MMORPG rodando na porta {PORT}...")
    print("Aguardando conexões...")
    
    while True:
        conn, addr = server.accept()
        thread.start_new_thread(tratar_cliente, (conn, addr))

except KeyboardInterrupt:
    print("\nServidor encerrado.")
    server.close()
    sys.exit()