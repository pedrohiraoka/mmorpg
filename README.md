# MMORPG em Python com Pygame

Um projeto de MMORPG simples desenvolvido em Python utilizando a biblioteca Pygame. O projeto inclui um servidor e cliente para multiplayer, geração de mapas e renderização de tiles e objetos.

## Estrutura do Projeto

```
projeto_mmorpg/
├── src/                    # Código fonte principal
│   ├── cliente.py          # Cliente completo com rede (Quadro 2)
│   ├── cliente_interativo.py  # Cliente com movimentação por teclado
│   ├── criar_imagens.py    # Script para gerar imagens placeholder
│   ├── exemplo_inicial.py  # Exemplo básico de inicialização do Pygame
│   ├── gerar_mapas.py      # Script para gerar mapas de exemplo
│   ├── renderizacao_basica.py  # Renderização básica sem interação
│   └── servidor.py         # Servidor multiplayer
├── data/                   # Dados do jogo (mapas)
│   ├── tilemap.txt         # Matriz de texturas do terreno
│   └── objmap.txt          # Matriz de objetos do mapa
├── imagens/                # Sprites do jogo
│   ├── tile0.png ... tile23.png   # Texturas do terreno
│   └── obj0.png ... obj23.png     # Objetos/personagens
├── scripts/                # Scripts utilitários
│   └── run.sh              # Script para iniciar servidor e clientes
└── docs/                   # Documentação
    └── estrutura.txt       # Descrição da estrutura de arquivos
```

## Pré-requisitos

- Python 2.x (devido ao uso de `cPickle` e `thread`)
- Pygame

## Como Executar

### 1. Gerar as imagens placeholder (opcional)

```bash
python src/criar_imagens.py
```

### 2. Gerar os mapas de exemplo

```bash
python src/gerar_mapas.py
```

### 3. Iniciar o servidor

Em um terminal:

```bash
python src/servidor.py
```

### 4. Iniciar o(s) cliente(s)

Em outro(s) terminal(is):

```bash
python src/cliente.py
```

Ou use o script de execução:

```bash
bash scripts/run.sh
```

## Controles

- **Setas do teclado**: Movimentam o personagem
- **Clique do mouse**: Obtém informações da posição clicada
- **Fechar janela**: Encerra o cliente

## Eventos do Jogo

- `GOTO (24)`: Movimentar personagem
- `MESSAGE (25)`: Mensagem do servidor para o cliente
- `SETOBJECT (26)`: Criar/destruir objeto no mapa
- `SYSTEM (27)`: Mensagens do sistema
- `GETINFO (28)`: Requisitar informações de um ponto do mapa

## Notas

- Este projeto foi desenvolvido para Python 2.x devido ao uso de módulos como `cPickle` e `thread`.
- Para Python 3.x, será necessário atualizar os imports (`cPickle` → `pickle`, `thread` → `_thread`).