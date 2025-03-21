from ursina import *
from math import sin, cos, radians

# Inicializar la aplicación
app = Ursina()

#Fondo y Centro de la órbita
window.color = color.black
background = Entity(model='quad', texture='textures/i.jpg', scale=8, double_sided=True, position=(0, 0, 1))
center = Entity(model='sphere', scale=0)

# Crear entidades para el Sol y los planetas
sol = Entity(model='quad', texture='textures/kelvin.jpg', scale=2, position=(0, 0, 0))
planetas = []

# Crear planetas con diferentes colores y posiciones iniciales
colores = [color.blue, color.red, color.green, color.orange]
distancias = [1.5, 2, 4, 6]
velocidades = [20, 10, 15, 25]

    #planeta = Entity(model='sphere', color=colores[i], scale=0.5, position=(distancias[i], 0, 0))
    #planetas.append(planeta)

# Función de actualización
def crear_planeta(colorp, distanciap):
    planeta = Entity(model='sphere', color=colorp, scale=0.5, position=(distanciap, 0, 0))
    #Generar los puntos del círculo
    points = []
    radius = distanciap
    num_segments = 100  # Número de segmentos para aproximar el círculo
    orbit_color = color.white
    for i in range(num_segments + 1):
        angle = i * 2 * math.pi / num_segments
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        points.append((x, y, 0))
    #Crear el LineRenderer
    orbit_line = Entity(model=Mesh(vertices=points, mode='line'), color=orbit_color)
    return planeta

for i in range(len(colores)):
    planetas.append(crear_planeta(colores[i], distancias[i]))

def update():
    for i, planeta in enumerate(planetas):
        # Rotación alrededor del Sol
        angulo = time.time() * velocidades[i]  # Velocidad de rotación
        planeta.x = distancias[i] * cos(radians(angulo))
        planeta.y = distancias[i] * sin(radians(angulo))
        # Rotación sobre su propio eje
        planeta.rotation_y += 100 * time.dt

# Ejecutar la aplicación
app.run()

