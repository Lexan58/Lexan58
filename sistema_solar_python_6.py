from ursina import Entity as OriginalEntity
import traceback
from ursina.vec3 import Vec3  # necesario porque aún no has importado todo

class DebugEntity(OriginalEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'texture', None) is None and self.position == Vec3(0, 0, 0):
            print("\n[DEBUG] Entidad sospechosa creada")
            print(f"Nombre: {self.name}, Modelo: {self.model}, Args: {args}, Kwargs: {kwargs}")
            print("Stack de creación:")
            traceback.print_stack(limit=5)

# Reemplazamos globalmente
import ursina
ursina.Entity = DebugEntity

# Reimportamos después de sobrescribir
from ursina import *  # ahora sí traerá el DebugEntity en lugar del original
import math
import random

# Inicializar la aplicación
app = Ursina()
window.color = color.black
camera.position = (0, 0, -50)
camera.rotation_x = 10

# Sonido de fondo
musica = Audio('sounds/space-chords-loop-310493.mp3', loop=True, autoplay=True)

# Fondo estrellado
background = Entity(model='quad', texture='2k_stars_milky_way', scale=50, double_sided=True, position=(0, 0, 1), render_queue=-1)

# Sol con halo luminoso
sol = Entity(model='sphere', texture='textures/2k_sun.jpg', scale=3, position=(0, 0, 0))
#sol_halo = Entity(model='sphere', color=color.rgba(255, 200, 0, 80), scale=3, position=(0, 0, 0))
light = PointLight(parent=sol, position=(0, 0, -2))
light2 = PointLight(parent=sol, position=(0, 0, 2))
light3 = PointLight(parent=sol, position=(0, 2, 0))
light4 = PointLight(parent=sol, position=(0, -2, 0))
light5 = PointLight(parent=sol, position=(-2, 0, 0))
light6 = PointLight(parent=sol, position=(2, 0, 0))

# Luz ambiental suave para mejorar visibilidad en planetas lejanos
ambient_light = AmbientLight()
ambient_light.color = color.rgba(150, 150, 150, 0.3)  # Luz tenue grisácea

# Luz direccional adicional desde el Sol hacia el sistema
sun_directional_light = DirectionalLight()
sun_directional_light.look_at(Vec3(1, -0.3, -1))  # Dirección diagonal hacia el fondo
sun_directional_light.color = color.rgba(255, 240, 200, 0.5)  # Tono cálido suave

# Verificar si hay entidades basura en el centro
def limpiar_basura_visual():
    for e in scene.entities:
        if e.position == Vec3(0, 0, 0) and e != sol:
            if not getattr(e, 'texture', None) and e.name == 'entity':
                print(f"[BASURA] Eliminando: {e}")
                destroy(e)

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
planeta_seleccionado = None

# Zoom suave
zoom_objetivo = -50
camera.z = zoom_objetivo

# Información de planeta
info = Text(text='', origin=(0, 4), background=True, scale=1.5)
simulacion_activa = True
orbita_activa = True

# Información tipo Wikipedia
info_expandida = [
    "Mercurio: El planeta más cercano al Sol y el más pequeño del sistema solar.",
    "Venus: Similar en tamaño a la Tierra, con una atmósfera densa y caliente.",
    "Tierra: Nuestro hogar, el único planeta conocido con vida.",
    "Marte: El planeta rojo, con evidencia de agua en el pasado.",
    "Júpiter: El planeta más grande, con una Gran Mancha Roja.",
    "Saturno: Famoso por sus impresionantes anillos.",
    "Urano: Un gigante helado que rota de lado.",
    "Neptuno: El planeta más lejano, conocido por sus vientos veloces."
]

# Botones de interfaz

botones = []
def seleccionar_planeta(i):
    global planeta_seleccionado
    planeta_seleccionado = planetas[i]
    info.text = f"{nombres[i]}\nDistancia: {distancias[i]} AU\nTamaño: {tamanos[i]}"
    for b in botones:
        b.color = color.azure
    botones[i].color = color.orange


for i, nombre in enumerate(nombres):
    btn = Button(text=nombre, position=Vec2(-0.8892508, 0.45) + Vec2(0.11, -0.07*i), scale=(0.2, 0.05), color=color.azure, 
                 on_click=Func(seleccionar_planeta, i))
    botones.append(btn)

# Panel de control lateral
boton_reset = Button(text='Reiniciar cámara', position=window.bottom_left + Vec2(0.11, 0.1), scale=(0.2, 0.05), color=color.red,
                     on_click=lambda: resetear_camara())
boton_orbitas = Button(text='Activar órbitas', position=window.bottom_left + Vec2(0.11, 0.03), scale=(0.2, 0.05), color=color.green,
                       on_click=lambda: alternar_orbitas())

# Botón para controlar la música
Button(text='Activar Música', position=Vec2(0.8, -0.45), scale=(0.2, 0.05), color=color.cyan, on_click=lambda: alternar_musica())

def resetear_camara():
    global planeta_seleccionado
    camera.rotation_x = 10
    camera.rotation_y = 0
    planeta_seleccionado = None
    info.text = ""

def alternar_orbitas():
    global orbita_activa
    orbita_activa = not orbita_activa

# Función para controlar la música
musica_activa = True
def alternar_musica():
    global musica_activa
    musica_activa = not musica_activa
    if musica_activa:
        musica.play()
    else:
        musica.stop()

# Funciones auxiliares para crear entidades 

# Función para crear órbitas, evitando la posición (0, 0, 0)
def crear_orbita(radius, planeta):
    if radius != 0:  # Solo crear órbitas si el radio no es 0
        num_puntos = 50
        puntos = [(radius * math.cos(2 * math.pi * i / num_puntos),
                   radius * math.sin(2 * math.pi * i / num_puntos), 0)
                  for i in range(num_puntos + 1)]
        
        # Crear la órbita solo si el radio es mayor que 0
        if radius > 0:
            Entity(model=Mesh(vertices=puntos, mode='line'), color=color.white, parent=planeta.parent)
        else:
            print(f"[DEBUG] Se evitó crear una órbita en el radio 0 para el planeta {planeta.name}.")

# Función para crear el planeta
def crear_planeta(nombre, textura, tamaño, distancia):
    # Crear el planeta
    planeta = Entity(model='sphere', texture=textura, scale=tamaño)
    
    # Si no tiene textura asignada, asignar una por defecto
    if planeta.texture is None:
        print(f"[DEBUG] El planeta {nombre} no tiene textura asignada, asignando textura por defecto.")
        planeta.texture = "default_texture"  # Cambiar a la textura que desees como predeterminada

    # Crear la órbita del planeta
    crear_orbita(distancia, planeta)

    return planeta

def crear_luna(color_luna, escala, planeta_objetivo, radio_orbita):
    return Entity(model='sphere', color=color_luna, scale=escala, position=(planeta_objetivo.x + radio_orbita, planeta_objetivo.y, 0))

def crear_asteroide():
    return Entity(model='sphere', color=color.gray, scale=0.1, position=(random.uniform(-20, 20), random.uniform(-10, 10), random.uniform(-5, 5)))

# Creación de planetas
planetas = []
for i in range(len(nombres)):
    planeta = crear_planeta(nombres[i], texturas[i], tamanos[i], distancias[i])
    planetas.append(planeta)

# Agregar lunas
lunas = [
    Entity(model='sphere', texture='textures/2k_moon.jpg', scale=0.15, position=(4.3, 0, 0)),  # Luna de la Tierra
    crear_luna(color.gray, 0.2, planetas[4], 0.5),    # Ganímedes (Júpiter)
    crear_luna(color.yellow, 0.15, planetas[5], 0.4), # Titán (Saturno)
]

# Anillo de Saturno
anillo = Entity(model='sphere', texture='textures/2k_saturn_ring_alpha.png', scale=(2, 2, 0), parent=planetas[5], rotation_x=90, render_queue=2)

# Asteroides
asteroides = [crear_asteroide() for _ in range(30)]

mouse_sensitivity = 200

# Rotación del Sol
sol_rotacion = 0

# Lógica de actualización

def update():
    global planeta_seleccionado, zoom_objetivo, sol_rotacion
    if not simulacion_activa:
        return

    #detectar_anomalia_visual()

    hovered_planeta = None
    tiempo = time.time()

    for i, planeta in enumerate(planetas):
        angulo = tiempo * velocidades[i]
        planeta.x = distancias[i] * math.cos(math.radians(angulo))
        planeta.y = distancias[i] * math.sin(math.radians(angulo))
        planeta.rotation_y += rotaciones_propias[i] * time.dt

        if mouse.hovered_entity == planeta:
            hovered_planeta = planeta

    texto.text = hovered_planeta.name if hovered_planeta else ("" if not planeta_seleccionado else texto.text)

    luna_angulo = tiempo * 50
    for i, (luna, planeta_idx, factor) in enumerate(zip(lunas, [2, 4, 5], [1, 0.5, 1/3])):
        angulo = math.radians(luna_angulo * factor)
        luna.x = planetas[planeta_idx].x + (0.5 + i * 0.3) * math.cos(angulo)
        luna.y = planetas[planeta_idx].y + (0.5 + i * 0.3) * math.sin(angulo)

    for asteroide in asteroides:
        asteroide.x += random.uniform(-0.01, 0.01)
        asteroide.y += random.uniform(-0.01, 0.01)
        asteroide.z += random.uniform(-0.01, 0.01)

    sol_rotacion += 5 * time.dt
    sol.rotation_y = sol_rotacion

    if held_keys['right mouse']:
        camera.rotation_y += mouse.velocity[0] * mouse_sensitivity
        camera.rotation_x -= mouse.velocity[1] * mouse_sensitivity

    destino = planeta_seleccionado.position if planeta_seleccionado else planetas[2].position
    camera.position = lerp(camera.position, destino + Vec3(0, 2, -10), 0.02)
    camera.z = lerp(camera.z, zoom_objetivo, 0.05)

# Manejo de entrada

def input(key):
    global planeta_seleccionado, zoom_objetivo, simulacion_activa, orbita_activa
    if key == 'scroll up': zoom_objetivo += 1
    elif key == 'scroll down': zoom_objetivo -= 1
    elif key == 'left mouse down':
        if mouse.hovered_entity in planetas:
            planeta_seleccionado = mouse.hovered_entity
            idx = planetas.index(planeta_seleccionado)
            info.text = f"{planeta_seleccionado.name}\n{info_expandida[idx]}\nDistancia: {distancias[idx]} AU\nTamaño: {tamanos[idx]}"
            for b in botones: b.color = color.azure
            botones[idx].color = color.orange
        else:
            info.text = ""
    elif key == 'q' and planeta_seleccionado:
        planeta_seleccionado.rotation_y += 50
    elif key == 'p':
        simulacion_activa = not simulacion_activa
    elif key == 'o':
        orbita_activa = not orbita_activa
    elif key == 'r':
        resetear_camara()
    elif key == 'l':  # por ejemplo, presionar la tecla "L"
        print("Entidades en escena:")
        for e in scene.entities:
          if e.position == Vec3(0, 0, 0) and hasattr(e, 'name') and e.name == "entity":
                e.color=color.red
                e.model="cube"
                print(f"{e} - Nombre: {e.name}, Posición: {e.position}")

"""def detectar_anomalia_visual():
    for e in scene.entities:
        if e.position == Vec3(0, 0, 0) and e != sol:
            if hasattr(e, 'texture') and not e.texture:
                print(f"[ALERTA] Entidad sin textura en (0, 0, 0): {e}, modelo: {e.model}, nombre: {e.name}")
                e.model = "cube"
                e.color = color.magenta
                e.name = "entidad_sospechosa"
            elif hasattr(e, 'color') and e.color == color.black:
                print(f"[ALERTA] Entidad negra en el centro: {e}, modelo: {e.model}")
                e.color = color.lime
                e.model = "cube"
                e.name = "entidad_sospechosa_color"

# Llama a la función dentro del update
def update():
    global planeta_seleccionado, zoom_objetivo, sol_rotacion
    if not simulacion_activa:
        return

    # Debug visual para identificar entidad sospechosa
    detectar_anomalia_visual()"""

app.run()