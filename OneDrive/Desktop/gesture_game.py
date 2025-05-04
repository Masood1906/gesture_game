import pygame
import random
import cv2
import mediapipe as mp

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Gesture Control Shooting Game")
clock = pygame.time.Clock()

# Game Variables
player = pygame.Rect(375, 520, 50, 60)
player_color = (0, 255, 0)
enemy_color = (255, 0, 0)
bullet_color = (255, 255, 0)
enemies = []
bullets = []
enemy_speed = 3
bullet_speed = 7
score = 0
font = pygame.font.SysFont('arial', 24)
game_over = False
can_shoot = True
shoot_cooldown = 20
shoot_timer = 0

# MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

# Functions
def spawn_enemy():
    x = random.randint(0, 750)
    enemies.append(pygame.Rect(x, -50, 50, 50))

def draw_text(text, x, y, color=(255, 255, 255)):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

# Main Game Loop
spawn_timer = 0
running = True

while running:
    screen.fill((0, 0, 0))
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and process frame
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Webcam Display (small)
    small_frame = cv2.resize(frame, (160, 120))
    small_surface = pygame.image.frombuffer(small_frame.tobytes(), (160, 120), "BGR")
    screen.blit(small_surface, (640, 10))

    keys = pygame.key.get_pressed()

    # Hand Movement → Move player
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        x = int(hand.landmark[mp_hands.HandLandmark.WRIST].x * 800)
        if x < player.x - 20:
            player.x -= 5
        elif x > player.x + 20:
            player.x += 5

    # Keep player on screen
    player.x = max(0, min(player.x, 750))

    # Shooting bullets
    if keys[pygame.K_SPACE] and can_shoot:
        bullets.append(pygame.Rect(player.centerx - 5, player.y, 10, 20))
        can_shoot = False
        shoot_timer = 0

    # Handle cooldown
    if not can_shoot:
        shoot_timer += 1
        if shoot_timer >= shoot_cooldown:
            can_shoot = True

    # Draw player
    pygame.draw.rect(screen, player_color, player)

    # Spawn enemies
    spawn_timer += 1
    if spawn_timer > 60:
        spawn_enemy()
        spawn_timer = 0

    # Move and draw enemies
    for enemy in enemies[:]:
        enemy.y += enemy_speed
        if enemy.y > 600:
            enemies.remove(enemy)
            score += 1
        if player.colliderect(enemy):
            game_over = True
        pygame.draw.rect(screen, enemy_color, enemy)

    # Move and draw bullets
    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)
        else:
            pygame.draw.rect(screen, bullet_color, bullet)
    shoot_timer += 1
    if shoot_timer > 15:  # 15 frames cooldown
        can_shoot = True


    # Bullet-enemy collision
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 5
                break

    # Difficulty increases
    if score % 10 == 0 and score != 0:
        enemy_speed = min(10, enemy_speed + 1)
        if score > 50:
            enemy_speed = 7  # Faster enemies after score reaches 50


    # Display score
    draw_text(f"Score: {score}", 10, 10)

    # Game Over
    if game_over:
        draw_text("GAME OVER", 330, 250, (255, 0, 0))
        draw_text("Press R to Restart or Q to Quit", 250, 300)
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_r]:
            enemies.clear()
            bullets.clear()
            score = 0
            enemy_speed = 3
            game_over = False
        elif keys[pygame.K_q]:
            running = False
        continue

    pygame.display.flip()
    clock.tick(60)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
