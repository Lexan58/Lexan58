from ursina import *
import math
import random

# Inicializar la aplicación
app = Ursina()
window.color = color.black
camera.position = (0, 0, -35)
camera.rotation_x = 10

# Sonido de fondo
musica = Audio('sounds/space-chords-loop-310493.mp3', loop=True, autoplay=True)

# Fondo estrellado
#background = Entity(model='quad', texture='textures/i.jpg', scale=12, double_sided=True, position=(0, 0, 1))

# Sol
sol = Entity(model='sphere', texture='textures/2k_sun.jpg', scale=3, position=(0, 0, 0))
light = PointLight(parent=sol, position=(0, 0, -2))
light2 = PointLight(parent=sol, position=(0, 0, 2))
light3 = PointLight(parent=sol, position=(0, 2, 0))
light4 = PointLight(parent=sol, position=(0, -2, 0))
light5 = PointLight(parent=sol, position=(-2, 0, 0))
light6 = PointLight(parent=sol, position=(2, 0, 0))


# Datos de los planetas
nombres = ["Mercurio", "Venus", "Tierra", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"]
texturas = [
    'textures/2k_mercury.jpg', 'textures/2k_venus_atmosphere.jpg', 'textures/2k_earth_daymap.jpg', 'textures/2k_mars.jpg',
    'textures/2k_jupiter.jpg', 'textures/2k_saturn.jpg', 'textures/2k_uranus.jpg', 'textures/2k_neptune.jpg'
]
tamanos = [0.3, 0.5, 0.55, 0.4, 1.2, 1.0, 0.8, 0.7]
distancias = [2, 3, 4, 5, 9, 12, 15, 18]
velocidades = [60, 45, 35, 30, 20, 15, 10, 5]
rotaciones_propias = [10, 5, 1, 2, 25, 20, 18, 16]

planetas = []
texto = Text("", position=(-0.7, 0.4), color=color.white, scale=2)

# Función para crear órbitas
def crear_orbita(radius):
    points = [(radius * math.cos(2 * math.pi * i / 100), radius * math.sin(2 * math.pi * i / 100)* 0.9, 0) for i in range(101)]
    return Entity(model=Mesh(vertices=points, mode='line'), color=color.white)

# Crear planetas
for i in range(len(nombres)):
    planeta = Entity(model='sphere', texture=texturas[i], scale=tamanos[i], position=(distancias[i], 0, 0))
    crear_orbita(distancias[i])
    planetas.append(planeta)

# Agregar lunas
lunas = [
    Entity(model='sphere', texture='textures/2k_moon.jpg', scale=0.15, position=(4.3, 0, 0)),  # Luna de la Tierra
    Entity(model='sphere', color=color.gray, scale=0.2, position=(9.5, 0, 0)),  # Ganímedes (Júpiter)
    Entity(model='sphere', color=color.yellow, scale=0.15, position=(12.8, 0, 0)),  # Titán (Saturno)
]

# Anillo de Saturno
anillo = Entity(model='sphere', texture='textures/2k_saturn_ring_alpha.png', scale=(2, 2, 0), parent=planetas[5], rotation_x=90)

# Estrellas
estrellas = [Entity(model='sphere', color=color.gray, scale=0.1, position=(random.uniform(-20, 20), random.uniform(-10, 10), random.uniform(-5, 5))) for _ in range(30)]

# Control camara
camera_x=0
camera_z=0
camera_distance = 10  # Distancia entre la cámara y el "sol"
camera_angle = 0  # Ángulo inicial de rotación

# Movimiento de la cámara con el mouse
def input(key):

    if key == 'scroll up':
        camera.position += (0, 0, 1)
    elif key == 'scroll down':
        camera.position -= (0, 0, 1)
    elif key == 'w':
        camera.position += (0, 1, 0)
    elif key == 's':
        camera.position -= (0, 1, 0)
    elif key == 'a':
        camera.position -= (1, 0, 0)
    elif key == 'd':
        camera.position += (1, 0, 0)
    elif key == 'q':
        #camera_angle -= 1
        print(camera_angle - 1)  
        print(camera_x)  
        print(camera_z)  
    elif key == 'e':
        #camera_angle += 1
        print(camera_angle)  


# Movimiento de los planetas y lunas
def update():
    global camera_angle
    planeta_detectado = False
    
    for i, planeta in enumerate(planetas):
        angulo = time.time() * velocidades[i]
        planeta.x = distancias[i] * math.cos(math.radians(angulo))
        planeta.y = distancias[i] * math.sin(math.radians(angulo)) * 0.9
        planeta.rotation_y += rotaciones_propias[i] * time.dt

        if mouse.hovered_entity == planeta:
            texto.text = nombres[i]
            planeta_detectado = True
    
    if not planeta_detectado:
        texto.text = ""


    camera_x = math.cos(math.radians(camera_angle)) * camera_distance
    camera_z = math.sin(math.radians(camera_angle)) * camera_distance
    #camera.position = (camera_x, 20, camera_z) 
    
    
    #camera.look_at(sol)  # Mantener el enfoque en el "sol"

    # Movimiento de las lunas
    luna_angulo = time.time() * 50
    lunas[0].x = planetas[2].x + 0.5 * math.cos(math.radians(luna_angulo))
    lunas[0].y = planetas[2].y + 0.5 * math.sin(math.radians(luna_angulo))
    lunas[1].x = planetas[4].x + 1.2 * math.cos(math.radians(luna_angulo / 2))
    lunas[1].y = planetas[4].y + 1.2 * math.sin(math.radians(luna_angulo / 2))
    lunas[2].x = planetas[5].x + 0.8 * math.cos(math.radians(luna_angulo / 3))
    lunas[2].y = planetas[5].y + 0.8 * math.sin(math.radians(luna_angulo / 3))
    
    # Movimiento de los estrellas
    for estrella in estrellas:
        estrella.x += random.uniform(-0.01, 0.01)
        estrella.y += random.uniform(-0.01, 0.01)
        estrella.z += random.uniform(-0.01, 0.01)
    
    # Cámara sigue la Tierra
    #camera.position = lerp(camera.position, planetas[2].position + Vec3(0, 2, -20), 0.02)
Cursor()
app.run()
