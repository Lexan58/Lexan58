from ursina import *
import math
import random

# Inicializar la aplicación Ursina
app = Ursina(
    title="Sistema Solar 3D",
    borderless=False,
    fullscreen=False,
    vsync=True,
    development_mode=False
)

# Configurar la pantalla
window.exit_button.visible = True
window.fps_counter.enabled = True

# Constantes
CAMERA_START_POS = (0, 0, -30)
CAMERA_START_ROT = (8, 0, 0)
MOUSE_SENSITIVITY = 200
MUSIC_FILE = 'sounds/space-chords-loop-310493.mp3'
BACKGROUND_SCALE = 100
SOL_SCALE = 3
SOL_LIGHT_OFFSET = 2

# Clases personalizadas
class CuerpoCeleste(Entity):
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
        num_puntos = 50
        puntos = []
        for i in range(num_puntos + 1):
            angle = 2 * math.pi * i / num_puntos
            x = self.distance * math.cos(angle)
            y = self.distance * math.sin(angle)
            puntos.append((x, y, 0))

        self.orbit = Entity(
            model=Mesh(vertices=puntos, mode='line'),
            color=color.white,
            position=(0, 0, 0),
            parent=scene,
            enabled=True,
            name=f"orbit_{self.name}"
        )

    def update_position(self, time_value, orbita_activa):
        angle = time_value * self.speed
        self.x = self.distance * math.cos(math.radians(angle))
        self.y = self.distance * math.sin(math.radians(angle))

        if self.orbit:
            self.orbit.enabled = orbita_activa

        self.rotation_y += self.rotation_speed * time.dt

class Luna(Entity):
    def __init__(self, planet, radius, speed_factor, **kwargs):
        if not planet:
            raise ValueError("El planeta debe existir antes de crear la luna")
            
        super().__init__(model='sphere', **kwargs)
        self.planet = planet
        self.radius = radius
        self.speed_factor = speed_factor
        self.update_position(0)

    def update_position(self, time_value):
        if not self.planet or not hasattr(self.planet, 'x') or not hasattr(self.planet, 'y'):
            return
            
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

        # Fondo estrellado
        Entity(
            model='quad', 
            texture='2k_stars_milky_way',
            scale=BACKGROUND_SCALE, 
            double_sided=True,
            position=(0, 0, 1)
        )

        # Sol
        self.sol = Entity(
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

        # Datos reales para mostrar en pantalla
        self.tamanos_reales = [4879, 12104, 12742, 6779, 139820, 116460, 50724, 49244]     # Diámetro en km
        self.distancias_reales = [57.9, 108.2, 149.6, 227.9, 778.6, 1433.5, 2872.5, 4495.1] # Distancia en millones de km

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

        # Crear lunas
        self.lunas = [
                Luna(self.planetas[2], 0.5, 1, texture='textures/2k_moon.jpg', scale=0.15),
                Luna(self.planetas[4], 0.5, 0.5, color=color.gray, scale=0.2),
                Luna(self.planetas[5], 0.4, 1/3, color=color.yellow, scale=0.15)
            ]
        
        # Anillo de Saturno
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
        self.info = Text(text='', origin=(0, 4), background=True, scale=1, 
                        max_lines=6, position=(0, -0.1))
        self.info.background.color = color.rgba(255, 255, 255, 0)       #Este es el circulo negro, no cambiar.

        # Sonido de fondo
        self.canciones = [
            Audio('sounds/space-chords-loop-310493.mp3', loop=True, autoplay=False),
            Audio('sounds/FuerzaRegidaGrupoFrontera-Coqueta.mp3', loop=True, autoplay=False),
            Audio('sounds/one-more-time-radio-edit.mp3', loop=True, autoplay=False),
            Audio('sounds/PabloAlborán-Saturno.mp3', loop=True, autoplay=False),
        ]

        self.titulos_canciones = ['sounds/space-chords-loop-310493.mp3', 'sounds/FuerzaRegidaGrupoFrontera-Coqueta.mp3', 
                                  'sounds/one-more-time-radio-edit.mp3', 'sounds/PabloAlborán-Saturno.mp3']
        self.cancion_actual = 0
        self.canciones[self.cancion_actual].play()

        self.nombres_canciones = ["Tema espacial", "Coqueta", "One More Time", "Saturno"]


    def siguiente_cancion(self):
        self.canciones[self.cancion_actual].pause()  # ❌ no uses .stop()
        self.cancion_actual = (self.cancion_actual + 1) % len(self.canciones)
        self.canciones[self.cancion_actual].play()

        self.boton_cancion.text = f"Cambiar música ({self.nombres_canciones[self.cancion_actual]})"

        if not self.musica_activa:
            self.canciones[self.cancion_actual].pause()


    def setup_ui(self):
        self.botones = []
        for i, nombre in enumerate(self.nombres):
            btn = Button(
                text=nombre, 
                position=Vec2(-0.8892508, 0.45) + Vec2(0.11, -0.07*i), 
                scale=(0.2, 0.05), 
                color=color.azure,
                on_click=Func(self.seleccionar_planeta, i)
            )
            self.botones.append(btn)

        self.boton_reset = Button(
            text='Reiniciar cámara', 
            position=Vec2(0.75, -0.26),
            scale=(0.23, 0.05), 
            color=color.pink,
            on_click=self.resetear_camara
        )

        self.boton_orbitas = Button(
            text='Activar órbitas', 
            position=Vec2(0.75, -0.14), 
            scale=(0.23, 0.05), 
            color=color.pink,
            on_click=self.alternar_orbitas
        )

        self.boton_musica = Button(
            text='Activar Música', 
            position=Vec2(0.75, -0.2), 
            scale=(0.23, 0.05), 
            color=color.pink,
            on_click=self.alternar_musica
        )

        self.boton_cancion = Button(
            text=f"Cambiar música ({self.nombres_canciones[self.cancion_actual]})",
            position=(0.6, 0.45),
            scale=(0.50, 0.04),
            color=color.pink,
            on_click=self.siguiente_cancion
        )

        self.boton_simulacion = Button(
            text='Pausar Simulación' if self.simulacion_activa else 'Reanudar Simulación',
            position=Vec2(0.75, -0.32), 
            scale=(0.23, 0.05), 
            color=color.pink,
            on_click=self.alternar_simulacion
        )

    def crear_asteroide(self):
        return Entity(
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
            nombre = self.nombres[index]
            distancia_real = self.distancias_reales[index]
            tamano_real = self.tamanos_reales[index]

            self.info.text = (f" {self.nombres[index]}\n"
            f" Distancia al Sol: {distancia_real} millones de km\n"
            f" Diámetro: {tamano_real} km"
            )


            for btn in self.botones:
                btn.color = color.azure
            self.botones[index].color = color.orange

        except Exception as e:
            print(f"Error en seleccionar_planeta(): {e}")

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
            if planeta.orbit:
                planeta.orbit.enabled = self.orbita_activa

    def alternar_musica(self):
        actual = self.canciones[self.cancion_actual]

        try:
            if actual.playing:
                actual.pause()
                self.musica_activa = False
                self.boton_musica.text = 'Activar música'
            else:
                actual.resume()
                self.musica_activa = True
                self.boton_musica.text = 'Desactivar música'
        except Exception as e:
            print(f"❌ Error al alternar música: {e}")

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
            except Exception as e:
                print(f"Error al actualizar planeta {i}: {e}")

        self.texto.text = hovered_planeta.name if hovered_planeta else ""

        # Actualizar lunas
        for luna in self.lunas:
            try:
                luna.update_position(self.tiempo_acumulado)
            except Exception as e:
                print(f"Error al actualizar luna: {e}")

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
            camera.rotation_x = max(min(camera.rotation_x, 90), -90)

        # Actualizar posición de la cámara
        if self.planeta_seleccionado:
            destino = self.planeta_seleccionado.position
        else:
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

app.run()