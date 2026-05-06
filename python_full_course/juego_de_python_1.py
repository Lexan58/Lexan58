import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Racer")
clock = pygame.time.Clock()

# Inicializar propiedades del jugador
player_x = WIDTH // 2
player_y = HEIGHT - 120
player_speed = 7
player_width, player_height = 60, 30  # Dimensiones del jugador

def move_player(keys, x):
    if keys[pygame.K_LEFT] and x > 0:
        x -= player_speed
    if keys[pygame.K_RIGHT] and x < WIDTH - player_width:
        x += player_speed
    return x

running = True
while running:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Actualizar posición del jugador
    keys = pygame.key.get_pressed()  # Obtener estado de las teclas
    player_x = move_player(keys, player_x)

    # Renderizado
    screen.fill((0, 0, 0))  # Limpiar pantalla (fondo negro)
    pygame.draw.rect(screen, (0, 255, 255), (player_x, player_y, player_width, player_height))  # Dibujar jugador
    pygame.display.flip()  # Actualizar pantalla

    clock.tick(60)  # 60 FPS

pygame.quit()