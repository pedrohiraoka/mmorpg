# MMORPG 2D em Python

Jogo MMORPG 2D completo desenvolvido em Python com Pygame, composto por cliente e servidor que se comunicam via sockets TCP.

## Estrutura do Projeto

```
projeto_mmorpg/
├── cliente.py          # Cliente com interface gráfica Pygame
├── servidor.py         # Servidor multithreaded centralizador
├── gerar_mapas.py      # Script para gerar mapas aleatórios
├── criar_imagens.py    # Script para gerar imagens de tiles e objetos
├── data/
│   ├── tilemap.txt     # Mapa de texturas (500x500)
│   └── objmap.txt      # Mapa de objetos (500x500)
└── imagens/
    ├── tile0.png até tile23.png
    └── obj0.png até obj23.png
```

## Requisitos

- Python 3.6+
- Pygame

Instale as dependências:

```bash
pip install pygame
```

## Como Executar

### Passo 1: Gerar Recursos

Primeiro, gere as imagens e os mapas do jogo:

```bash
cd projeto_mmorpg
python criar_imagens.py
python gerar_mapas.py
```

Isso criará:
- 24 imagens de tiles (tile0.png - tile23.png) na pasta `imagens/`
- 24 imagens de objetos (obj0.png - obj23.png) na pasta `imagens/`
- Arquivo `tilemap.txt` com o mapa de texturas 500x500
- Arquivo `objmap.txt` com o mapa de objetos 500x500

### Passo 2: Iniciar o Servidor

Em um terminal, execute o servidor:

```bash
python servidor.py
```

O servidor irá:
- Escutar na porta 5000 em todas as interfaces (0.0.0.0)
- Aceitar múltiplas conexões de clientes
- Gerenciar o estado do mundo e sincronizar jogadores

### Passo 3: Conectar Clientes

Em outros terminais (um para cada jogador), execute o cliente:

```bash
python cliente.py
```

Você pode executar múltiplos clientes simultaneamente para testar o multiplayer.

## Controles do Jogo

| Tecla/Ação | Função |
|------------|--------|
| ↑ (Seta Cima) | Mover para cima |
| ↓ (Seta Baixo) | Mover para baixo |
| ← (Seta Esquerda) | Mover para esquerda |
| → (Seta Direita) | Mover para direita |
| Combinação de setas | Movimento diagonal |
| Clique do mouse | Obter informação da posição clicada |
| ESC | Sair do jogo |

## Funcionalidades

### Servidor
- ✅ Multithreaded (uma thread por cliente)
- ✅ Validação de movimentos dentro dos limites do mapa (0-499)
- ✅ Sincronização de entrada/saída de jogadores
- ✅ Atualização de posições em tempo real
- ✅ Resposta a requisições de informação (GETINFO)
- ✅ Tratamento adequado de desconexões

### Cliente
- ✅ Interface gráfica com Pygame (640x480 pixels)
- ✅ Renderização de mapa 500x500 com sistema de câmera
- ✅ Sistema de tiles e objetos em camadas
- ✅ Movimentação suave com teclas direcionais
- ✅ Visualização de outros jogadores em tempo real
- ✅ Exibição de mensagens na parte inferior da tela
- ✅ Thread listener para receber atualizações do servidor

## Arquitetura de Comunicação

A comunicação entre cliente e servidor é baseada em eventos serializados com pickle:

| Tipo | ID | Descrição |
|------|-----|-----------|
| GOTO | 24 | Movimentação do jogador |
| MESSAGE | 25 | Mensagem exibida ao jogador |
| SETOBJECT | 26 | Criar/destruir objeto no mapa |
| SYSTEM | 27 | Mensagem do sistema |
| GETINFO | 28 | Requisitar informação de posição |
| MYID | 29 | Apresentação do jogador ao conectar |

## Fluxo de Conexão

1. Cliente conecta ao servidor na porta 5000
2. Cliente envia evento MYID com seu ID e nome
3. Servidor posiciona jogador em (250, 250)
4. Servidor envia ao novo cliente todos os jogadores existentes
5. Servidor notifica todos os outros sobre o novo jogador
6. Servidor envia mensagem de boas-vindas

## Fluxo de Movimentação

1. Jogador pressiona tecla direcional
2. Cliente calcula nova posição e envia GOTO ao servidor
3. Servidor valida se está dentro dos limites (0-499)
4. Servidor remove personagem da posição antiga (SETOBJECT com obj=255)
5. Servidor atualiza posição no dicionário
6. Servidor adiciona personagem na nova posição (SETOBJECT)
7. Servidor confirma movimento ao cliente com GOTO
8. Cliente atualiza câmera para centralizar na nova posição

## Limitações Técnicas

- Mapa fixo de 500x500 tiles
- Cada tile tem 40x40 pixels
- Janela de 640x480 pixels (16x11 tiles visíveis + área de texto)
- Limite de 7 FPS intencional para reduzir tráfego de rede
- Máximo de 10 conexões pendentes no servidor

## Solução de Problemas

### "Servidor recusou conexão"
Verifique se o servidor está rodando antes de iniciar o cliente.

### "Imagens não encontradas"
Execute `python criar_imagens.py` para gerar as imagens.

### "Mapas não encontrados"
Execute `python gerar_mapas.py` para gerar os mapas.

### Erro de permissão na porta 5000
Em alguns sistemas, portas abaixo de 1024 requerem privilégios. Use outra porta editando a constante `PORTA` no servidor e `SERVIDOR_PORTA` no cliente.

## Desenvolvimento

Este projeto foi desenvolvido seguindo as melhores práticas Python:
- Código bem comentado em português
- Classes e funções com docstrings
- Tratamento adequado de exceções
- Separação clara de responsabilidades
- Thread-safe com locks para acesso concorrente

## Licença

Projeto educacional livre para uso e modificação.
