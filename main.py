import pygame
import os
import subprocess
import time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 640, 480  # dein 2.8" DPI Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini TV Menü")
font = pygame.font.Font(None, 30)

# --- Farben ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# --- Filme laden ---
VIDEO_FOLDER = "/home/pi/tvprojekt/videos"
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]
videos.sort()

# --- Seiten ---
current_page = 0
videos_per_page = 8

# --- Double-tap exit ---
last_tap_time = 0
DOUBLE_TAP_THRESHOLD = 0.4  # Sekunden

def double_tap_detected():
    global last_tap_time
    now = time.time()
    if now - last_tap_time < DOUBLE_TAP_THRESHOLD:
        return True
    last_tap_time = now
    return False

def play_video(filepath):
    # Start VLC as subprocess and allow double-tap exit while playing
    proc = subprocess.Popen(["cvlc", "--play-and-exit", "--fullscreen", filepath])
    running_video = True
    global last_tap_time
    while running_video:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                proc.terminate()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if double_tap_detected():
                    proc.terminate()
                    return False
        # Optional: update a "playing..." overlay
        pygame.time.wait(50)
        if proc.poll() is not None:  # VLC exited
            running_video = False
    return True

# --- Hauptloop ---
running = True
while running:
    screen.fill(BLACK)

    # --- Überschrift ---
    title = font.render("== Menü ==", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))

    # --- Videos anzeigen ---
    start = current_page * videos_per_page
    end = start + videos_per_page
    for i, video in enumerate(videos[start:end]):
        text = font.render(f"{i+1}. {video}", True, WHITE)
        screen.blit(text, (20, 50 + i * 30))

    # --- Pfeile zeichnen (groß & touchbar) ---
    pygame.draw.polygon(screen, WHITE, [(20, 280), (60, 300), (20, 320)])  # links
    pygame.draw.polygon(screen, WHITE, [(460, 280), (420, 300), (460, 320)])  # rechts

    pygame.display.flip()

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Double-tap exit from menu
            if double_tap_detected():
                running = False
                break

            # Touch: Links (zurück)
            if x < 80 and 280 < y < 320:
                if current_page > 0:
                    current_page -= 1

            # Touch: Rechts (weiter)
            elif x > 400 and 280 < y < 320:
                if (current_page + 1) * videos_per_page < len(videos):
                    current_page += 1

            # Touch: Video auswählen
            for i in range(videos_per_page):
                tx, ty = 20, 50 + i * 30
                if tx < x < WIDTH and ty < y < ty + 30:
                    index = start + i
                    if index < len(videos):
                        filename = videos[index]
                        filepath = os.path.join(VIDEO_FOLDER, filename)
                        still_running = play_video(filepath)
                        if not still_running:
                            running = False
                        break