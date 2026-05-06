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
    development_mode=False
)

# Configurar la pantalla al inicio
window.exit_button.visible = True
window.fps_counter.enabled = True

import traceback

# DEBUGGING AVANZADO - Interceptar TODAS las creaciones de Entity
original_entity_init = Entity.__init__

def debug_entity_init(self, *args, **kwargs):
    # Llamar al constructor original
    original_entity_init(self, *args, **kwargs)

    # Criterios para una entidad sospechosa en (0,0,0)
    is_suspicious_model = hasattr(self, 'model') and self.model in ('sphere', 'circle')
    is_at_origin = hasattr(self, 'position') and self.position == Vec3(0, 0, 0)
    has_no_texture = hasattr(self, 'texture') and self.texture is None
    # También considerar blanco si no hay textura, ya que Ursina puede usarlo por defecto
    is_default_color_or_clear = hasattr(self, 'color') and (self.color == color.black or self.color == color.clear or self.color == color.white)
    # Excluir el sol si ya tiene un nombre específico
    is_not_sol = not (hasattr(self, 'name') and self.name == 'SOL_PRINCIPAL')
    # Excluir el Skybox (el fondo de estrellas)
    is_not_sky = not isinstance(self, Sky)

    if is_suspicious_model and is_at_origin and has_no_texture and is_default_color_or_clear and is_not_sol and is_not_sky:
        print('\n🚨 ENTIDAD SOSPECHOSA DETECTADA Y DESTRUIDA:')
        print(f' - Modelo: {self.model}')
        print(f' - Textura: {self.texture}')
        print(f' - Color: {self.color}')
        print(f' - Posición: {self.position}')
        print(f' - Escala: {self.scale}')
        print(' - Stack trace (Origen de la creación):')
        traceback.print_stack(limit=8) # Aumentar el límite para ver más contexto

        try:
            destroy(self)
            print('🔥 DESTRUIDA CON ÉXITO.')
        except Exception as e:
            print(f'❌ ERROR AL DESTRUIR LA ENTIDAD: {e}')

# Aplicar el debugging
Entity.__init__ = debug_entity_init
# Constantes
WINDOW_COLOR = color.black
CAMERA_START_POS = (0, 0, -50)
CAMERA_START_ROT = (10, 0, 0)
MOUSE_SENSITIVITY = 200
MUSIC_FILE = 'sounds/space-chords-loop-310493.mp3'
BACKGROUND_SCALE = 50
SOL_SCALE = 3
SOL_LIGHT_OFFSET = 2

# Clase para órbitas seguras
class OrbitaSegura:
    def __init__(self, distance):
        self.distance = distance
        self.enabled = True
        self.lines = []
        self.create_orbit()
    
    def create_orbit(self):
        # Crear órbita usando múltiples líneas cortas para evitar círculos negros
        num_segments = 72  # Más segmentos para suavidad
        
        for i in range(num_segments):
            angle1 = 2 * math.pi * i / num_segments
            angle2 = 2 * math.pi * (i + 1) / num_segments
            
            x1 = self.distance * math.cos(angle1)
            y1 = self.distance * math.sin(angle1)
            x2 = self.distance * math.cos(angle2)
            y2 = self.distance * math.sin(angle2)
            
            # Usar Entity con configuración muy específica
            line = Entity(
                model=Mesh(vertices=[Vec3(x1, y1, 0), Vec3(x2, y2, 0)], mode='line'),
                color=color.rgba(255, 255, 255, 150),
                unlit=True,
                position=(0, 0, -0.1),  # Ligeramente atrás para evitar z-fighting
                always_on_top=False
            )
            self.lines.append(line)
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        for line in self.lines:
            if line:
                line.enabled = enabled

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
        self.orbit_segura = OrbitaSegura(distance)

    def update_position(self, time_value, orbita_activa):
        # Actualizar posición del planeta
        if orbita_activa:
            angle = time_value * self.speed
            self.x = self.distance * math.cos(math.radians(angle))
            self.y = self.distance * math.sin(math.radians(angle))
        
        # Actualizar rotación del planeta
        self.rotation_y += self.rotation_speed * time.dt
        
        # Controlar visibilidad de órbita
        if self.orbit_segura:
            self.orbit_segura.set_enabled(orbita_activa)

class Luna(Entity):
    def __init__(self, planet, radius, speed_factor, **kwargs):
        if not planet:
            raise ValueError("El planeta debe existir antes de crear la luna")
            
        super().__init__(
            model='sphere',
            **kwargs
        )
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


        # Sonido de fondo
        try:
            self.musica = Audio(MUSIC_FILE, loop=True, autoplay=True, volume=0.5)
            print("Música cargada correctamente")
        except Exception as e:
            print(f"Error al cargar la música: {e}")
            self.musica = None
            self.musica_activa = False

        # Fondo estrellado
        Entity(
            model='quad', 
            texture='2k_stars_milky_way',
            scale=BACKGROUND_SCALE, 
            double_sided=True,
            position=(0, 0, 1)
        )

        # Sol - MUY ESPECÍFICO para evitar confusión
        self.sol = Entity(
            model='sphere', 
            texture='textures/2k_sun.jpg',
            scale=SOL_SCALE, 
            position=(0, 0, 0),
            name='SOL_PRINCIPAL'  # Nombre específico
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
        self.info = Text(text='', origin=(0, 4), background=True, scale=1.5)


    def setup_ui(self):
        self.botones = []
        for i, nombre in enumerate(self.nombres):
            btn = Button(
                text=nombre,
                position=window.top_left + Vec2(0.1, -0.05*i),
                scale=0.1,
                color=color.azure,
                on_click=Func(self.seleccionar_planeta, i)
            )
            self.botones.append(btn)

        self.boton_reset = Button(
            text='Reiniciar cámara',
            position=window.bottom_left + Vec2(0.1, 0.1),
            scale=0.1,
            color=color.red,
            on_click=self.resetear_camara
        )

        self.boton_orbitas = Button(
            text='Desactivar órbitas' if self.orbita_activa else 'Activar órbitas',
            position=window.bottom_left + Vec2(0.1, 0.0),
            scale=0.1,
            color=color.green,
            on_click=self.alternar_orbitas
        )

        self.boton_musica = Button(
            text='Desactivar Música' if self.musica_activa else 'Activar Música',
            position=window.bottom_left + Vec2(0.1, -0.1),
            scale=0.1,
            color=color.cyan,
            on_click=self.alternar_musica
        )

        self.boton_simulacion = Button(
            text='Pausar Simulación' if self.simulacion_activa else 'Reanudar Simulación',
            position=window.bottom_left + Vec2(0.1, -0.2),
            scale=0.1,
            color=color.yellow,
            on_click=self.alternar_simulacion
        )

        # BOTÓN ESPECIAL PARA LIMPIAR CÍRCULOS NEGROS
        self.boton_limpiar = Button(
            text='Limpiar círculos',
            position=window.bottom_left + Vec2(0.1, -0.3),
            scale=0.1,
            color=color.red,
            on_click=self.limpiar_circulos_negros
        )

    def limpiar_circulos_negros(self):
        """Función especial para eliminar círculos negros problemáticos"""
        eliminados = 0
        for entity in scene.entities.copy():  # Usar copy() para evitar modificar lista mientras iteramos
            try:
                if (hasattr(entity, 'model') and entity.model == 'circle' and
                    hasattr(entity, 'texture') and entity.texture is None and
                    hasattr(entity, 'position') and entity.position == Vec3(0, 0, 0) and
                    hasattr(entity, 'name') and entity.name != 'SOL_PRINCIPAL'):
                    
                    print(f'🧹 Eliminando círculo negro: {entity}')
                    destroy(entity)
                    eliminados += 1
            except Exception as e:
                print(f"Error al verificar entidad: {e}")
        
        print(f"✅ Eliminados {eliminados} círculos negros")

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
        self.planeta_seleccionado = self.planetas[index]
        self.info.text = f"{self.nombres[index]}\n{self.info_expandida[index]}\nDistancia: {self.distancias[index]} AU\nTamaño: {self.tamanos[index]}"

        for btn in self.botones:
            btn.color = color.azure
        self.botones[index].color = color.orange

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
            if hasattr(planeta, 'orbit_segura') and planeta.orbit_segura:
                planeta.orbit_segura.set_enabled(self.orbita_activa)
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

        #Actualizar Planetas
     

        # Actualizar lunas
        if hasattr(self, 'lunas'):
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
        elif key == 'c':  # Nueva tecla para limpiar círculos
            self.limpiar_circulos_negros()

# Crear y ejecutar el sistema solar
sistema_solar = SistemaSolar()

def update():
    sistema_solar.update()

def input(key):
    sistema_solar.input(key)

def escanear_entidades_en_camara():
    print("\n🔍 Escaneo de entidades potencialmente vinculadas a la cámara o invisibles:")
    for e in scene.entities:
        if e.position == Vec3(0, 0, 0):
            print(f"👀 En (0,0,0): {e}, model={e.model}, texture={e.texture}, color={e.color}, parent={e.parent}, billboard={getattr(e, 'billboard', False)}")
        if getattr(e, 'parent', None) == camera:
            print(f"📸 Vinculada a cámara: {e}, model={e.model}, texture={e.texture}, color={e.color}")
        if getattr(e, 'billboard', False):
            print(f"🎯 Billboard activo: {e}, model={e.model}, texture={e.texture}, color={e.color}")

escanear_entidades_en_camara()

def eliminar_circulo_cog_menu():
    for e in scene.entities:
        if e.name == "cog_menu_info" and e.model == "circle":
            print("🧹 Eliminando el círculo negro de cog_menu_info")
            destroy(e)
eliminar_circulo_cog_menu()

app.run()