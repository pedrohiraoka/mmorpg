# gerar_mapas.py - Para criar mapas de exemplo
import cPickle
import random

# Cria mapa de texturas 500x500 com valores aleatórios (0-23)
tilemap = [[random.randint(0, 23) for x in range(500)] for y in range(500)]

# Cria mapa de objetos 500x500 (255 = vazio)
objmap = [[255 for x in range(500)] for y in range(500)]
# Adiciona alguns objetos de exemplo (IDs 0-14 nas bordas para teste)
for i in range(500):
    objmap[0][i] = random.randint(0, 14)
    objmap[499][i] = random.randint(0, 14)
    objmap[i][0] = random.randint(0, 14)
    objmap[i][499] = random.randint(0, 14)

# Salva arquivos
cPickle.dump(tilemap, file('data/tilemap.txt', 'w'))
cPickle.dump(objmap, file('data/objmap.txt', 'w'))

print("Mapas gerados com sucesso!")