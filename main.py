import pygame
import os
import subprocess
import time
import getpass


# --- Setup ---asdjhra
pygame.init()
WIDTH, HEIGHT = 640, 480  # Landscape
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.display.set_caption("Mini TV Menü")
font = pygame.font.Font(None, 42)

# --- Farben ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (102, 0, 153) 

# --- Filme laden ---
VIDEO_FOLDER = "/home/pi/tvprojekt/videos"
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
videos = [f for f in os.listdir(VIDEO_FOLDER) if (f.endswith(".mp4")) or (f.endswith(".mov")) or (f.endswith(".mkv"))]
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
    proc = subprocess.Popen([
        "mpv",
        "--fs",                    # Fullscreen
        "--no-border",             # No window border
        "--autofit=640x480",       # Resize to fit screen
        "--ontop",                 # Stay on top
        "--really-quiet",          # No console output
        "--osc=no",                # (Optional) Hide on-screen controls
        "--keepaspect=yes",        # Keep video aspect ratio
        "--no-keepaspect-window", # Keep aspect ratio for the window
        filepath
    ])
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
        pygame.time.wait(50)
        if proc.poll() is not None:  # mpv exited
            running_video = False
    return True

def fix_runtime_dir_permissions():
    runtime_dir = f"/run/user/{os.getuid()}"
    if os.path.exists(runtime_dir):
        os.chmod(runtime_dir, 0o700)

# --- Hauptloop ---
running = True
while running:
    screen.fill(PURPLE)

    # --- Überschrift ---
    title = font.render("== Menü ==", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))

    # --- Videos anzeigen ---
    start = current_page * videos_per_page
    end = start + videos_per_page
    for i, video in enumerate(videos[start:end]):
        text = font.render(f"{i+1}. {video}", True, WHITE)
        screen.blit(text, (60, 60 + i * 40))

    # --- Pfeile zeichnen (groß & touchbar) ---
    pygame.draw.polygon(screen, WHITE, [(20, HEIGHT//2-40), (60, HEIGHT//2), (20, HEIGHT//2+40)])  # links
    pygame.draw.polygon(screen, WHITE, [(WIDTH-20, HEIGHT//2-40), (WIDTH-60, HEIGHT//2), (WIDTH-20, HEIGHT//2+40)])  # rechts

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
            if x < 80 and (HEIGHT//2-40) < y < (HEIGHT//2+40):
                if current_page > 0:
                    current_page -= 1

            # Touch: Rechts (weiter)
            elif x > WIDTH-80 and (HEIGHT//2-40) < y < (HEIGHT//2+40):
                if (current_page + 1) * videos_per_page < len(videos):
                    current_page += 1

            # Touch: Video auswählen
            for i in range(videos_per_page):
                tx, ty = 60, 60 + i * 40
                if tx < x < WIDTH-60 and ty < y < ty + 40:
                    index = start + i
                    if index < len(videos):
                        filename = videos[index]
                        filepath = os.path.join(VIDEO_FOLDER, filename)
                        fix_runtime_dir_permissions()  # Fix permissions before playing video
                        still_running = play_video(filepath)
                        if not still_running:
                            running = False
                        break 
