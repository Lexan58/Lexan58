from ursina import *
import math
import random
from ursina.prefabs.first_person_controller import FirstPersonController

# Inicializar la aplicación Ursina
app = Ursina(
    title="Sistema Solar 3D",
    borderless=False,
    fullscreen=False,
    vsync=True,
    development_mode=False  # Desactivar desarrollo para mayor rendimiento
)

# Configurar la pantalla al inicio
window.exit_button.visible = True  # Botón para cerrar la aplicación
window.fps_counter.enabled = True  # Mostrar FPS

import traceback

# Guardar una referencia a la clase Entity original antes de reemplazarla
from ursina import Entity as OriginalEntity

class DebugEntity(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Detectar esferas sospechosas en el centro sin textura
        if (
            self.model in ('sphere', 'circle')
            and self.texture is None
            and self.position == Vec3(0, 0, 0)
        ):
            print('\n🕵️ Círculo negro creado:')
            print(' - Model:', self.model)
            print(' - Texture:', self.texture)
            print(' - Position:', self.position)
            print(' - Args:', args)
            print(' - Kwargs:', kwargs)
            print(' - Clase:', self.__class__)
            traceback.print_stack(limit=8)

# Constantes
WINDOW_COLOR = color.black
CAMERA_START_POS = (0, 0, -30)
CAMERA_START_ROT = (8, 0, 0)
MOUSE_SENSITIVITY = 200
MUSIC_FILE = 'sounds/space-chords-loop-310493.mp3'
BACKGROUND_SCALE = 100
SOL_SCALE = 3
SOL_LIGHT_OFFSET = 2

# Clases personalizadas
class CuerpoCeleste(Entity):  # Volver a usar Entity normal
    def __init__(self, name, texture, scale, distance, speed, rotation_speed, **kwargs):
        super().__init__(
            model='sphere',
            texture=texture,
            scale=scale,
            position=(distance, 0, 0),
            name=name,
            **kwargs
        )
        self.distance = distance
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.orbit = None
        self.create_orbit()

    def create_orbit(self):
        # Crear puntos para la órbita circular
        num_puntos = 50
        puntos = []
        for i in range(num_puntos + 1):
            angle = 2 * math.pi * i / num_puntos
            x = self.distance * math.cos(angle)
            y = self.distance * math.sin(angle)
            puntos.append((x, y, 0))
                   
        # Crear la órbita como una entidad separada (no como hija del planeta)
        self.orbit = Entity(  # Volver a usar Entity normal
            model=Mesh(vertices=puntos, mode='line'),
            color=color.white,
            position=(0, 0, 0),  # La órbita se centra en el origen (0,0,0)
            thickness=1
        )

    def update_position(self, time_value, orbita_activa):
        # Actualizar posición del planeta
        if orbita_activa:
            angle = time_value * self.speed
            self.x = self.distance * math.cos(math.radians(angle))
            self.y = self.distance * math.sin(math.radians(angle))
        
        # Actualizar rotación del planeta
        self.rotation_y += self.rotation_speed * time.dt

class Luna(Entity):  # Volver a usar Entity normal
    def __init__(self, planet, radius, speed_factor, **kwargs):
        # Asegurarse de que el planeta ya esté creado antes de crear la luna
        if not planet:
            raise ValueError("El planeta debe existir antes de crear la luna")
            
        super().__init__(
            model='sphere',
            **kwargs
        )
        self.planet = planet
        self.radius = radius
        self.speed_factor = speed_factor
        # Inicializar en una posición válida
        self.update_position(0)

    def update_position(self, time_value):
        if not self.planet or not hasattr(self.planet, 'x') or not hasattr(self.planet, 'y'):
            return  # No actualizar si el planeta no es válido
            
        angle = math.radians(time_value * 50 * self.speed_factor)
        self.x = self.planet.x + self.radius * math.cos(angle)
        self.y = self.planet.y + self.radius * math.sin(angle)

# Sistema Solar
class SistemaSolar:
    def __init__(self):
        self.simulacion_activa = True
        self.orbita_activa = True
        self.musica_activa = True
        self.planeta_seleccionado = None
        self.zoom_objetivo = -50
        self.sol_rotacion = 0
        self.tiempo_acumulado = 0

        self.setup_escena()
        self.setup_ui()

    def setup_escena(self):
        # Configurar cámara
        camera.position = CAMERA_START_POS
        camera.rotation = CAMERA_START_ROT
        
        # Sonido de fondo
        try:
            self.musica = Audio(MUSIC_FILE, loop=True, autoplay=True, volume=0.5)
            print("Música cargada correctamente")
        except Exception as e:
            print(f"Error al cargar la música: {e}")
            self.musica = None
            self.musica_activa = False

        # Fondo estrellado - Usar OriginalEntity para evitar el círculo negro
        OriginalEntity(
            model='quad', 
            texture='2k_stars_milky_way',
            scale=BACKGROUND_SCALE, 
            double_sided=True,
            position=(0, 0, 1)
        )

        # Sol - Usar OriginalEntity solo para el sol para evitar círculos negros
        self.sol = OriginalEntity(
            model='sphere', 
            texture='textures/2k_sun.jpg',
            scale=SOL_SCALE, 
            position=(0, 0, 0)
        )

        # Luces alrededor del sol
        for pos in [(0,0,-SOL_LIGHT_OFFSET), (0,0,SOL_LIGHT_OFFSET),
                    (0,SOL_LIGHT_OFFSET,0), (0,-SOL_LIGHT_OFFSET,0),
                    (-SOL_LIGHT_OFFSET,0,0), (SOL_LIGHT_OFFSET,0,0)]:
            PointLight(parent=self.sol, position=pos)

        # Luz ambiental
        AmbientLight(color=color.rgba(150, 150, 150, 0.3))

        # Luz direccional
        DirectionalLight(
            look_at=Vec3(1, -0.3, -1),
            color=color.rgba(255, 240, 200, 0.5)
        )

        # Datos de los planetas
        self.nombres = ["Mercurio", "Venus", "Tierra", "Marte",
                                   "Júpiter", "Saturno", "Urano", "Neptuno"]
        self.texturas = [
            'textures/2k_mercury.jpg', 'textures/2k_venus_atmosphere.jpg',
            'textures/2k_earth_daymap.jpg', 'textures/2k_mars.jpg',
            'textures/2k_jupiter.jpg', 'textures/2k_saturn.jpg',
            'textures/2k_uranus.jpg', 'textures/2k_neptune.jpg'
        ]
        self.tamanos = [0.3, 0.5, 0.55, 0.4, 1.2, 1.0, 0.8, 0.7]
        self.distancias = [2, 3, 4, 5, 9, 12, 15, 18]
        self.velocidades = [60, 45, 35, 30, 20, 15, 10, 5]
        self.rotaciones = [10, 5, 1, 2, 25, 20, 18, 16]

                # Crear planetas
        self.planetas = []
        for i in range(len(self.nombres)):
            planeta = CuerpoCeleste(
                name=self.nombres[i],
                texture=self.texturas[i],
                scale=self.tamanos[i],
                distance=self.distancias[i],
                speed=self.velocidades[i],
                rotation_speed=self.rotaciones[i]
            )
            self.planetas.append(planeta)

        # Crear lunas (después de crear los planetas)
        self.lunas = []
        try:
            self.lunas = [
                Luna(self.planetas[2], 0.5, 1, texture='textures/2k_moon.jpg', scale=0.15),
                Luna(self.planetas[4], 0.5, 0.5, color=color.gray, scale=0.2),
                Luna(self.planetas[5], 0.4, 1/3, color=color.yellow, scale=0.15)
            ]
        except Exception as e:
            print(f"Error al crear lunas: {e}")
            # Continuar sin lunas si hay un error

        # Anillo de Saturno - Volver a usar Entity normal
        Entity(
            model='sphere', 
            texture='textures/2k_saturn_ring_alpha.png',
            scale=(2, 2, 0), 
            parent=self.planetas[5], 
            rotation_x=90
        )

        # Asteroides
        self.asteroides = [self.crear_asteroide() for _ in range(30)]

        # UI
        self.texto = Text("", position=(-0.7, 0.4), color=color.white, scale=2)
        self.info = Text(text='', origin=(0, 4), background=True, scale=1.5, max_lines=6, position=(0.5, 0.4)) #Este es el ciculo negro
        print("✅ self.info creado correctamente:", self.info)


        # Minimapa
        self.setup_minimapa()

    def setup_minimapa(self):
        self.minimapa = Entity(  # Volver a usar Entity normal
            model='quad', 
            texture='white_cube',
            color=color.rgba(255,255,255,50),
            position=window.bottom_right - Vec2(0.15, 0.15),
            scale=(0.3, 0.3)
        )

        self.planeta_iconos = []
        for i, planeta in enumerate(self.planetas):
            icono = Entity(  # Volver a usar Entity normal
                model='circle', 
                color=color.random_color(),
                scale=0.015, 
                position=(0, 0, -0.1),
                parent=self.minimapa
            )
            icono.x = (self.distancias[i] / 20) - 0.15
            icono.y = planeta.y / 20 # Se usa la posición y del planeta para el icono
            self.planeta_iconos.append(icono)

    def setup_ui(self):
        self.botones = []
        for i, nombre in enumerate(self.nombres):
            btn = Button(text=nombre, position=Vec2(-0.8892508, 0.45)
                + Vec2(0.11, -0.07*i), scale=(0.2, 0.05), color=color.azure,
                on_click=Func(self.seleccionar_planeta, i)
            )
            self.botones.append(btn)

        self.boton_reset = Button(text='Reiniciar cámara', 
            position=window.bottom_left + Vec2(0.11, 0.1),
            scale=(0.2, 0.05), color=color.red,
            on_click=self.resetear_camara
        )

        self.boton_orbitas = Button(text='Activar órbitas', 
            position=window.bottom_left + Vec2(0.11, 0.03), 
            scale=(0.2, 0.05), color=color.green,
            on_click=self.alternar_orbitas
        )

        self.boton_musica = Button(text='Activar Música', 
            position=Vec2(0.8, -0.45), scale=(0.2, 0.05), color=color.cyan,
            on_click=self.alternar_musica
        )

        self.boton_simulacion = Button(
            text='Pausar Simulación' if self.simulacion_activa else 'Reanudar Simulación',
            position=Vec2(0.79, -0.38), scale=(0.23, 0.05), color=color.orange,
            on_click=self.alternar_simulacion
        )

    def crear_asteroide(self):
        return Entity(  # Volver a usar Entity normal
            model='sphere',
            color=color.gray,
            scale=0.1,
            position=(
                random.uniform(-20, 20),
                random.uniform(-10, 10),
                random.uniform(-5, 5)
            )
        )

    def seleccionar_planeta(self, index):
        try:
            self.planeta_seleccionado = self.planetas[index]

            if hasattr(self, 'info') and isinstance(self.info, Text):
                nombre = self.nombres[index]
                distancia = self.distancias[index]
                tamano = self.tamanos[index]
                texto = f"{nombre} Distancia: {distancia} AU, Tamano: {tamano}"
            
                if len(texto) > 300:
                    texto = texto[:297] + '...'
                self.info.text = texto
            else:
                print("⚠️ 'self.info' no existe o no es un objeto Text válido.")

            for btn in self.botones:
                btn.color = color.azure
            self.botones[index].color = color.orange

        except Exception as e:
            print(f"❌ Error en seleccionar_planeta(): {e}")


    def resetear_camara(self):
        camera.rotation_x = CAMERA_START_ROT[0]
        camera.rotation_y = CAMERA_START_ROT[1]
        self.planeta_seleccionado = None
        self.info.text = ""
        self.zoom_objetivo = -50

    def alternar_orbitas(self):
        self.orbita_activa = not self.orbita_activa
        self.boton_orbitas.text = 'Desactivar órbitas' if self.orbita_activa else 'Activar órbitas'

        for planeta in self.planetas:
            if hasattr(planeta, 'orbit') and planeta.orbit:
                planeta.orbit.enabled = self.orbita_activa
                print(f"Órbita de {planeta.name}: {'activada' if self.orbita_activa else 'desactivada'}")

    def alternar_musica(self):
        self.musica_activa = not self.musica_activa
        self.boton_musica.text = 'Desactivar Música' if self.musica_activa else 'Activar Música'
        
        if hasattr(self, 'musica') and self.musica:
            try:
                if self.musica_activa:
                    self.musica.play()
                    print("Música activada")
                else:
                    self.musica.stop()
                    print("Música desactivada")
            except Exception as e:
                print(f"Error al controlar la música: {e}")

    def alternar_simulacion(self):
        self.simulacion_activa = not self.simulacion_activa
        self.boton_simulacion.text = 'Pausar Simulación' if self.simulacion_activa else 'Reanudar Simulación'

    def update(self):
        if not self.simulacion_activa:
            return

        self.tiempo_acumulado += time.dt

        # Actualizar planetas
        hovered_planeta = None
        for i, planeta in enumerate(self.planetas):
            try:
                planeta.update_position(self.tiempo_acumulado, self.orbita_activa)

                if mouse.hovered_entity == planeta:
                    hovered_planeta = planeta

                # Actualizar minimapa
                if hasattr(self, 'planeta_iconos') and i < len(self.planeta_iconos):
                    self.planeta_iconos[i].x = (planeta.x / 20) - 0.15
                    self.planeta_iconos[i].y = planeta.y / 20
            except Exception as e:
                print(f"Error al actualizar planeta {i}: {e}")
                # Continuar con el siguiente planeta si hay un error

        self.texto.text = hovered_planeta.name if hovered_planeta else ""

        # Actualizar lunas
        if hasattr(self, 'lunas'):
            for luna in self.lunas:
                try:
                    luna.update_position(self.tiempo_acumulado)
                except Exception as e:
                    print(f"Error al actualizar luna: {e}")
                    # Continuar con la siguiente luna si hay un error

        # Actualizar asteroides
        for asteroide in self.asteroides:
            asteroide.x += random.uniform(-0.01, 0.01)
            asteroide.y += random.uniform(-0.01, 0.01)
            asteroide.z += random.uniform(-0.01, 0.01)

        # Rotación del sol
        self.sol_rotacion += 5 * time.dt
        self.sol.rotation_y = self.sol_rotacion

        # Control de cámara
        if held_keys['right mouse']:
            camera.rotation_y += mouse.velocity[0] * MOUSE_SENSITIVITY * time.dt
            camera.rotation_x -= mouse.velocity[1] * MOUSE_SENSITIVITY * time.dt
            camera.rotation_x = max(min(camera.rotation_x, 90), -90)  # Limitar rotación en eje X

        # Actualizar posición de la cámara
        if self.planeta_seleccionado:
            destino = self.planeta_seleccionado.position
        else:
            # Si no hay planeta seleccionado, usar la Tierra o la posición (0,0,0)
            destino = self.planetas[2].position if len(self.planetas) > 2 else Vec3(0,0,0)
            
        if destino:
            camera.position = lerp(camera.position, destino + Vec3(0, 2, -10), 0.02)
            camera.z = lerp(camera.z, self.zoom_objetivo, 0.05)

    def input(self, key):
        if key == 'scroll up':
            self.zoom_objetivo += 1
        elif key == 'scroll down':
            self.zoom_objetivo -= 1
        elif key == 'left mouse down':
            if mouse.hovered_entity in self.planetas:
                index = self.planetas.index(mouse.hovered_entity)
                self.seleccionar_planeta(index)
            else:
                self.info.text = ""
        elif key == 'q' and self.planeta_seleccionado:
            self.planeta_seleccionado.rotation_y += 50
        elif key == 'p':
            self.alternar_simulacion()
        elif key == 'o':
            self.alternar_orbitas()
        elif key == 'r':
            self.resetear_camara()

# Crear y ejecutar el sistema solar
sistema_solar = SistemaSolar()

def update():
    sistema_solar.update()

def input(key):
    sistema_solar.input(key)

# Eliminar cualquier entidad "invisible" sospechosa en el centro
"""for e in scene.entities:
    if e.position == Vec3(0,0,0) and (not hasattr(e, 'texture') or e.texture is None):
        print('Eliminando entidad negra sospechosa:', e)
        destroy(e)"""

app.run()