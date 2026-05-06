from ursina import *
import math
import random

# =============================
#       Parámetros Globales
# =============================
NUM_SEGMENTOS = 100  # Número de puntos para dibujar la órbita
CAMERA_SPEED = 1
CAMERA_DISTANCE = 10  # Distancia desde el origen para actualizar la cámara

# =============================
#     Inicializar la Aplicación
# =============================
app = Ursina()
window.color = color.black
camera.position = (0, 0, -35)
camera.rotation_x = 10

# =============================
#    Sonido y Fondo
# =============================
musica = Audio('sounds/space-chords-loop-310493.mp3', loop=True, autoplay=True)
# background = Entity(model='quad', texture='textures/i.jpg', scale=12, double_sided=True, position=(0, 0, 1))

# =============================
#           Sol y Luces
# =============================
sol = Entity(model='sphere', texture='textures/2k_sun.jpg', scale=3, position=(0, 0, 0))
# Se agregan varias PointLights para simular una iluminación ambiental alrededor del sol.
for pos in [(0, 0, -2), (0, 0, 2), (0, 2, 0), (0, -2, 0), (-2, 0, 0), (2, 0, 0)]:
    PointLight(parent=sol, position=pos)

# =============================
#       Datos de los Planetas
# =============================
nombres = ["Mercurio", "Venus", "Tierra", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"]
texturas = [
    'textures/2k_mercury.jpg', 
    'textures/2k_venus_atmosphere.jpg', 
    'textures/2k_earth_daymap.jpg', 
    'textures/2k_mars.jpg',
    'textures/2k_jupiter.jpg', 
    'textures/2k_saturn.jpg', 
    'textures/2k_uranus.jpg', 
    'textures/2k_neptune.jpg'
]
tamanos = [0.3, 0.5, 0.55, 0.4, 1.2, 1.0, 0.8, 0.7]
distancias = [2, 3, 4, 5, 9, 12, 15, 18]
velocidades = [60, 45, 35, 30, 20, 15, 10, 5]
rotaciones_propias = [10, 5, 1, 2, 25, 20, 18, 16]

planetas = []
# Texto para mostrar el nombre del planeta cuando se pase el cursor
texto = Text("", position=(-0.7, 0.4), color=color.white, scale=2)

# Variable para guardar el ángulo de la cámara (para efectos de giro si se desea)
camera_angle = 0

# =============================
#     Funciones Auxiliares
# =============================
def crear_orbita(radius):
    """Crea una órbita con 'NUM_SEGMENTOS' puntos."""
    points = [(radius * math.cos(2 * math.pi * i / NUM_SEGMENTOS),
               radius * math.sin(2 * math.pi * i / NUM_SEGMENTOS) * 0.9,
               0)
              for i in range(NUM_SEGMENTOS + 1)]
    return Entity(model=Mesh(vertices=points, mode='line'), color=color.white)

def actualizar_planeta(planeta, distancia, velocidad, rotacion_propia):
    """Actualiza la posición y rotación del planeta en su órbita."""
    angulo = time.time() * velocidad
    planeta.x = distancia * math.cos(math.radians(angulo))
    planeta.y = distancia * math.sin(math.radians(angulo)) * 0.9
    planeta.rotation_y += rotacion_propia * time.dt

# =============================
#        Creación de Planetas
# =============================
for i in range(len(nombres)):
    planeta = Entity(
        model='sphere',
        texture=texturas[i],
        scale=tamanos[i],
        position=(distancias[i], 0, 0),
        name=nombres[i]
    )
    # Se crea la órbita correspondiente para efectos visuales.
    crear_orbita(distancias[i])
    planetas.append(planeta)

# =============================
#            Lunas
# =============================
lunas = [
    # Luna de la Tierra.
    Entity(model='sphere', texture='textures/2k_moon.jpg', scale=0.15, position=(4.3, 0, 0)),
    # Ganímedes (Júpiter).
    Entity(model='sphere', color=color.gray, scale=0.2, position=(9.5, 0, 0)),
    # Titán (Saturno).
    Entity(model='sphere', color=color.yellow, scale=0.15, position=(12.8, 0, 0)),
]

# =============================
#         Anillo de Saturno
# =============================
anillo = Entity(
    model='sphere',
    texture='textures/2k_saturn_ring_alpha.png',
    scale=(2, 2, 0),
    parent=planetas[5],
    rotation_x=90
)

# =============================
#       Creación de Estrellas
# =============================
estrellas = [
    Entity(
        model='sphere',
        color=color.gray,
        scale=0.1,
        position=(random.uniform(-20, 20), random.uniform(-10, 10), random.uniform(-5, 5))
    )
    for _ in range(30)
]

# =============================
#          Control de Cámara
# =============================
def input(key):
    global camera_angle
    # Control de zoom y desplazamiento horizontal/vertical con WASD y scroll.
    if key == 'scroll up':
        camera.position += (0, 0, CAMERA_SPEED)
    elif key == 'scroll down':
        camera.position -= (0, 0, CAMERA_SPEED)
    elif key == 'w':
        camera.position += (0, CAMERA_SPEED, 0)
    elif key == 's':
        camera.position -= (0, CAMERA_SPEED, 0)
    elif key == 'a':
        camera.position -= (CAMERA_SPEED, 0, 0)
    elif key == 'd':
        camera.position += (CAMERA_SPEED, 0, 0)
    # Teclas 'q' y 'e' para ajustar el ángulo de la cámara (por ahora, solo se imprimen los valores)
    elif key == 'q':
        camera_angle -= 1
        print("camera_angle:", camera_angle)
    elif key == 'e':
        camera_angle += 1
        print("camera_angle:", camera_angle)

# =============================
#   Movimiento y Actualización
# =============================
def update():
    # Actualiza cada planeta
    for i, planeta in enumerate(planetas):
        actualizar_planeta(planeta, distancias[i], velocidades[i], rotaciones_propias[i])
        # Si se pasa el cursor sobre un planeta, se muestra su nombre
        if mouse.hovered_entity == planeta:
            texto.text = planeta.name
            break
    else:
        # Si ningún planeta está siendo sobrevolado, se borra el texto
        texto.text = ""
        
    # Actualiza la posición de las lunas (movimiento orbital simple)
    luna_angulo = time.time() * 50
    lunas[0].x = planetas[2].x + 0.5 * math.cos(math.radians(luna_angulo))
    lunas[0].y = planetas[2].y + 0.5 * math.sin(math.radians(luna_angulo))
    lunas[1].x = planetas[4].x + 1.2 * math.cos(math.radians(luna_angulo / 2))
    lunas[1].y = planetas[4].y + 1.2 * math.sin(math.radians(luna_angulo / 2))
    lunas[2].x = planetas[5].x + 0.8 * math.cos(math.radians(luna_angulo / 3))
    lunas[2].y = planetas[5].y + 0.8 * math.sin(math.radians(luna_angulo / 3))
    
    # Actualiza el movimiento de las estrellas (efecto sutil de movimiento aleatorio)
    for estrella in estrellas:
        estrella.x += random.uniform(-0.01, 0.01)
        estrella.y += random.uniform(-0.01, 0.01)
        estrella.z += random.uniform(-0.01, 0.01)
    
    # (Opcional) Si deseas que la cámara se oriente hacia el sol, descomenta lo siguiente:
    # camera.look_at(sol)

Cursor()
app.run()
