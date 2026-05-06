from ursina import *
import math

# Constantes
NUM_SEGMENTOS = 100

# Inicializar la aplicación
app = Ursina()

# Fondo y centro de la órbita
window.color = color.black

# Ajuste de cámara para abarcar todo el sistema
camera.position = (0, 0, -25)  # Alejar la cámara para ver todas las órbitas

background = Entity(
    model='quad', texture='textures/i.jpg', scale=12,
    double_sided=True, position=(0, 0, 1)
)
center = Entity(model='sphere', scale=0)

# Crear entidad para el Sol
sol = Entity(model='quad', texture='textures/kelvin.jpg', scale=2, position=(0, 0, 0))

# Parámetros para planetas
colores = [color.gray, color.orange, color.blue, color.red, color.brown, color.yellow, color.light_gray, color.azure]
distancias = [1, 1.5, 2, 2.5, 3.5, 4.5, 5.5, 6.5]
velocidades = [60, 45, 35, 30, 20, 15, 10, 5]  # Velocidades en función de la cercanía al Sol
planetas = []

def crear_orbita(radius):
    # Genera los puntos del círculo con list comprehension
    points = [
        (
            center.x + radius * math.cos(2 * math.pi * i / NUM_SEGMENTOS),
            center.y + radius * math.sin(2 * math.pi * i / NUM_SEGMENTOS),
            0
        )
        for i in range(NUM_SEGMENTOS + 1)
    ]
    # Crear el LineRenderer para la órbita
    return Entity(model=Mesh(vertices=points, mode='line'), color=color.white)

def crear_planeta(colorp, distanciap):
    # Crear el planeta y su órbita
    planeta = Entity(model='sphere', color=colorp, scale=0.5, position=(distanciap, 0, 0))
    orbit_line = crear_orbita(distanciap)
    return planeta

# Crear planetas
for clr, dist in zip(colores, distancias):
    planetas.append(crear_planeta(clr, dist))

def update():
    # Actualizar posición y rotación de cada planeta
    for i, planeta in enumerate(planetas):
        angulo = time.time() * velocidades[i]
        # Calcular posición usando coseno y seno (convertir a radianes)
        planeta.x = distancias[i] * math.cos(math.radians(angulo))
        planeta.y = distancias[i] * math.sin(math.radians(angulo))
        planeta.rotation_y += 100 * time.dt

app.run()
