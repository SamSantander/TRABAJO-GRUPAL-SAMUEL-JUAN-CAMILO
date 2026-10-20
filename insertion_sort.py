"""
Animación de Insertion Sort con pygame y bisect.

Dos modos (tecla M para cambiar):
    1) Insertion Sort clásico  -> busca la posición comparando hacia la izquierda
    2) Insertion Sort binario  -> busca la posición con bisect.bisect_right

Controles:
    ESPACIO -> pausar / reanudar
    M       -> cambiar de modo (reinicia con la misma lista)
    R       -> lista nueva
    ARRIBA / ABAJO -> velocidad
    ESC     -> salir
"""

import bisect
import random
import sys

import pygame

ANCHO, ALTO = 1000, 600
CANTIDAD = 50
MARGEN_SUP = 90

FONDO = (18, 18, 28)
AZUL = (90, 120, 200)
VERDE = (70, 190, 120)
AMARILLO = (240, 200, 60)
ROJO = (230, 70, 70)
MORADO = (200, 120, 230)
TEXTO = (235, 235, 245)


def insertion_clasico(lista, stats):
    n = len(lista)
    yield {"fase": "inicio", "ordenado": 1, "clave": None, "cmp": None}
    for i in range(1, n):
        j = i
        yield {"fase": "clave", "ordenado": i, "clave": i, "cmp": None}
        while j > 0:
            stats["comparaciones"] += 1
            yield {"fase": "comparar", "ordenado": i, "clave": j, "cmp": j - 1}
            if lista[j - 1] > lista[j]:
                lista[j - 1], lista[j] = lista[j], lista[j - 1]
                stats["movimientos"] += 1
                yield {"fase": "mover", "ordenado": i, "clave": j - 1, "cmp": j}
                j -= 1
            else:
                break
        yield {"fase": "insertado", "ordenado": i + 1, "clave": j, "cmp": None}
    yield {"fase": "fin", "ordenado": n, "clave": None, "cmp": None}


def insertion_binario(lista, stats):
    n = len(lista)
    yield {"fase": "inicio", "ordenado": 1, "clave": None, "cmp": None}
    for i in range(1, n):
        clave = lista[i]
        yield {"fase": "clave", "ordenado": i, "clave": i, "cmp": None}

        pos = bisect.bisect_right(lista, clave, 0, i)  # búsqueda O(log n)
        stats["comparaciones"] += max(1, i.bit_length())
        yield {"fase": "bisect", "ordenado": i, "clave": i, "cmp": pos}

        for j in range(i, pos, -1):
            lista[j] = lista[j - 1]
            lista[j - 1] = clave
            stats["movimientos"] += 1
            yield {"fase": "mover", "ordenado": i, "clave": j - 1, "cmp": j}

        lista[pos] = clave
        yield {"fase": "insertado", "ordenado": i + 1, "clave": pos, "cmp": None}
    yield {"fase": "fin", "ordenado": n, "clave": None, "cmp": None}


MODOS = [
    ("Insertion Sort clásico", insertion_clasico),
    ("Insertion Sort binario (bisect)", insertion_binario),
]

MENSAJES = {
    "inicio": "Listo para comenzar",
    "clave": "Tomando el siguiente elemento (amarillo)",
    "comparar": "Comparando con el elemento de la izquierda (rojo)",
    "bisect": "bisect.bisect_right encontró la posición (rojo)",
    "mover": "Desplazando / intercambiando (morado)",
    "insertado": "Elemento insertado en su lugar",
    "fin": "¡Lista ordenada! Presiona R o M",
}


def iniciar(base, modo):
    lista = base[:]
    stats = {"comparaciones": 0, "movimientos": 0}
    gen = MODOS[modo][1](lista, stats)
    estado = {"fase": "inicio", "ordenado": 0, "clave": None, "cmp": None}
    return lista, stats, gen, estado


def dibujar(pantalla, fuente, lista, estado, stats, modo, vel, pausado):
    pantalla.fill(FONDO)
    n = len(lista)
    ancho_barra = ANCHO / n
    alto_util = ALTO - MARGEN_SUP - 10
    maximo = max(lista)

    for idx, valor in enumerate(lista):
        color = AZUL
        if idx < estado["ordenado"] or estado["fase"] == "fin":
            color = VERDE
        if idx == estado["cmp"] and estado["fase"] in ("comparar", "bisect"):
            color = ROJO
        if idx == estado["cmp"] and estado["fase"] == "mover":
            color = MORADO
        if idx == estado["clave"]:
            color = AMARILLO
        alto = int(valor / maximo * alto_util)
        rect = pygame.Rect(int(idx * ancho_barra) + 1, ALTO - alto,
                           max(1, int(ancho_barra) - 2), alto)
        pygame.draw.rect(pantalla, color, rect)

    lineas = [
        MODOS[modo][0],
        MENSAJES[estado["fase"]],
        f"Comparaciones: {stats['comparaciones']}   Movimientos: {stats['movimientos']}   "
        f"Velocidad: {vel} pasos/s",
        f"ESPACIO: {'reanudar' if pausado else 'pausar'} | M: modo | R: nueva lista | ↑/↓: velocidad",
    ]
    for k, t in enumerate(lineas):
        pantalla.blit(fuente.render(t, True, TEXTO), (15, 6 + k * 20))


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Insertion Sort - pygame + bisect")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("consolas", 17)

    base = random.sample(range(1, CANTIDAD + 1), CANTIDAD)
    modo = 0
    lista, stats, gen, estado = iniciar(base, modo)
    vel, pausado, terminado, acc = 30, False, False, 0.0

    while True:
        dt = reloj.tick(120) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_SPACE:
                    pausado = not pausado
                elif e.key == pygame.K_UP:
                    vel = min(1000, vel + 10)
                elif e.key == pygame.K_DOWN:
                    vel = max(1, vel - 10)
                elif e.key == pygame.K_m:
                    modo = (modo + 1) % len(MODOS)
                    lista, stats, gen, estado = iniciar(base, modo)
                    terminado, pausado = False, False
                elif e.key == pygame.K_r:
                    base = random.sample(range(1, CANTIDAD + 1), CANTIDAD)
                    lista, stats, gen, estado = iniciar(base, modo)
                    terminado, pausado = False, False

        if not pausado and not terminado:
            acc += dt * vel
            while acc >= 1:
                acc -= 1
                try:
                    estado = next(gen)
                except StopIteration:
                    terminado = True
                    break

        dibujar(pantalla, fuente, lista, estado, stats, modo, vel, pausado)
        pygame.display.flip()


if __name__ == "__main__":
    main()