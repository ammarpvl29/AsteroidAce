import pygame, os, platform, random, sys
from pygame.locals import *
from math import *
from pygame import Vector2

# Diambil dari https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/13790741#13790741 yaitu cara memanipulasi directory path dan
# absolute path agar setelah mengkonversi .py ke .exe, .exe bisa mereferensikannya ke assets
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if platform.system() == 'Windows':
    os.environ['SDL_VIDEODRIVER'] = 'windib'

# Membuat referensi gambar dari nilai RGB untuk hitam, putih, dan hijau
HITAM = (0, 0, 0)
PUTIH = (255, 255, 255)
HIJAU = (0, 255, 0)
MERAH_MUDA = (255, 166, 201)

# Menginisialisasikan jendela (window) game
UKURAN_WINDOW = LEBAR_WINDOW, TINGGI_WINDOW = 640, 480
LEBAR_PESAWAT, TINGGI_PESAWAT = 17, 21
LEBAR_ASTEROID, TINGGI_ASTEROID = 51, 41
JUMLAH_ASTEROID = 3
NUM_OF_ROCK_SPLIT = 5
TINGKAT_ASTEROID_BARU = 300
TAMBAH_KECEPATAN = 6
KURANGI_KECEPATAN = 13
KECEPATAN_MAKS = 200.0

# Fungsi nilai yang menciptakan bentuk asteroid
BENTUK_ASTEROID = [(5,0), (0,15), (0,30),
              (15,40), (20,30), (30,40),
              (45,30), (45,25), (25,20),
              (45,10), (36,0), (25,5)]

# Fungsi untuk exit game
def exit():
    pygame.quit()
    sys.exit()

# Fungsi start game dengan menekan tombol apapun
def press_any_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                return

# Fungsi untuk membuat teks   
def bikin_text(text, font, surface, pos, color=HIJAU):
    model_text = font.render(text, 1, color)
    surface.blit(model_text, pos)

# Fungsi untuk ledakan
def efek_ledakan():
    ledakan = {'speed': KECEPATAN_MAKS * 3,
             'pos': Vector2(200, 150),
             'rot': 0.0,
             'surf': pygame.Surface((3, 11))}
    pygame.draw.aaline(ledakan['surf'], PUTIH, [1, 0], [1, 10])
    return ledakan

# Fungsi untuk membuat asteroid baru
def objek_asteroid():
    asteroid = {'speed': random.randint(20, 80),
            'pos': Vector2(random.randint(0, LEBAR_WINDOW - LEBAR_ASTEROID),
                           random.randint(0, TINGGI_WINDOW - TINGGI_ASTEROID)),
            'rot': 0.0,
            'rot_speed': random.randint(90, 180) / 1.0,
            'rot_direction': random.choice([-1, 1]),
            'surf': pygame.Surface((LEBAR_ASTEROID, TINGGI_ASTEROID)),
            'rect': pygame.Rect(0, 0, LEBAR_ASTEROID, TINGGI_ASTEROID),
            'hits': 0}
    pygame.draw.polygon(asteroid['surf'], PUTIH, BENTUK_ASTEROID, 1)
    return asteroid

# Fungsi untuk membuat model pesawat dan mengapply posisinya menggunakan vektor (realtime position)
def objek_pesawat():
    pesawat = {'speed': 0,
            'pos': Vector2(200, 150),
            'rot': 0.0,
            'rot_speed': 360.0,
            'surf': pygame.Surface((LEBAR_PESAWAT, TINGGI_PESAWAT)),
            'new': True}

    pygame.draw.aaline(pesawat['surf'], HIJAU, [0, 20], [8, 0])
    pygame.draw.aaline(pesawat['surf'], HIJAU, [8, 0], [16, 20])
    pygame.draw.aaline(pesawat['surf'], HIJAU, [2, 15], [7, 15])
    pygame.draw.aaline(pesawat['surf'], HIJAU, [14, 15], [9, 15])
    return pesawat

# Fungsi untuk mengubah posisi x dan y pesawat
def efek_rotasi(image, w, h):
    """Returns the drawing position and where it's heading"""
    pusat_x = sin(image['rot'] * pi / 180.0) # Diubah derajat ke radius lalu dihitung nilai x
    pusat_y = cos(image['rot'] * pi / 180.0) # Sama seperti diatas tetapi dicar nilai y-nya
    return Vector2(image['pos'].x - w / 2, image['pos'].y - h / 2), Vector2(pusat_x, pusat_y)

# Main loop, untuk inisiasi game Asteroid Ace
def main():
    pygame.init()
    screen = pygame.display.set_mode(UKURAN_WINDOW)    
    pygame.display.set_caption("Asteroid Ace")

    font_url = resource_path('sumber_font.ttf')
    text_url = resource_path('sumber_font.ttf')
    welcome_sound_url = resource_path('efek_suara_retro_01.wav')
    blaster_sound_url = resource_path('ledakan.wav')
    asteroid_hit_sound_url = resource_path('efek_kena_asteroid.wav')
    player_collision_sound_url = resource_path('efek_mati.wav')
    
    font_untuk_title = pygame.font.Font(font_url, 72)
    text_font = pygame.font.Font(text_url, 36)
    score_font = pygame.font.Font(None, 72)

    welcome_sound = pygame.mixer.Sound(welcome_sound_url)
    blaster_sound = pygame.mixer.Sound(blaster_sound_url)
    asteroid_hit_sound = pygame.mixer.Sound(asteroid_hit_sound_url)
    player_collision_sound = pygame.mixer.Sound(player_collision_sound_url)

    screen_rect = screen.get_rect()
    ship = objek_pesawat()    
    blasts = []
    score = 0
    num_of_lives = 3    
    total_time_passed_secs = 0    
    rock_add_counter = 0    
    running = True

    # Disini title game akan muncul dan akan menunggu user untuk menekan suatu tombol 
    title_rect = font_untuk_title.render('Asteroid Ace', 1, HIJAU).get_rect()
    start_rect = text_font.render('Tekan Tombol Apapun', 1, HIJAU).get_rect()
    bikin_text('Asteroid Ace', font_untuk_title, screen,
              (screen_rect.centerx - title_rect.width / 2,
               screen_rect.centery - (title_rect.height + start_rect.height + 10) / 2))
    bikin_text('Tekan Tombol Apapun', text_font, screen,
              (screen_rect.centerx - start_rect.width / 2,
               screen_rect.centery + 10))
    global top_score
    if top_score > 0:
        bikin_text('Top score: %s' % str(top_score), text_font, screen, (20, 10), MERAH_MUDA)
    pygame.display.update()
    welcome_sound.play()
    press_any_key()
    clock = pygame.time.Clock()

    rocks = []
    for i in range(JUMLAH_ASTEROID):
        rock = objek_asteroid()        
        rocks.append(rock)

    ## Game loop ##
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        pressed_keys = pygame.key.get_pressed()
        rot_direction = 0.0
        mov_direction = -1

        if pressed_keys[K_ESCAPE]:
            exit()
        if pressed_keys[K_a]: 
            rot_direction = +1.0        
        elif pressed_keys[K_d]:
            rot_direction = -1.0        
        if pressed_keys[K_w]:
            ship['speed'] += TAMBAH_KECEPATAN
            if ship['speed'] > KECEPATAN_MAKS: ship['speed'] = KECEPATAN_MAKS
        elif pressed_keys[K_s]:
            ship['speed'] -= KURANGI_KECEPATAN
            if ship['speed'] < 0: ship['speed'] = 0
        if pressed_keys[K_SPACE]:
            new_blast = efek_ledakan()
            new_blast['pos'] = Vector2(ship['pos'].x, ship['pos'].y)
            new_blast['rot'] = ship['rot']
            blasts.append(new_blast)
            blaster_sound.play()

        screen.fill(HITAM)
        time_passed = clock.tick(30)
        time_passed_secs = time_passed / 1000.0        
        total_time_passed_secs += time_passed_secs

        rock_add_counter += 1
        if rock_add_counter == TINGKAT_ASTEROID_BARU:
            rock_add_counter = 0
            rock = objek_asteroid()
            rock['pos'] = Vector2(0 - LEBAR_ASTEROID, random.randint(0, TINGGI_WINDOW - TINGGI_ASTEROID))
            rocks.append(rock)

        # Fungsi for loop untuk tembakan
        for blast in blasts[:]:            
            # Tembakan yang tidak berotasi terhadap posisi x dan y pesawat
            rotated_blast_surf = pygame.transform.rotate(blast['surf'], blast['rot'])

            # Jika iya buat fungsi baru untuk mendapat size
            bw, bh = rotated_blast_surf.get_size()

            # Membuat fungsi agar tembakan pesawat linear dengan posisi pesawat real time
            blast_draw_pos, b_heading = efek_rotasi(blast, bw, bh)
            b_heading *= mov_direction

            # Projectile tembakan akan sesuai real time
            blast['pos'] += b_heading * time_passed_secs * blast['speed']

            # Jika tembakannya keluar dari jendela maka akan diremove dari list
            if blast['pos'].y < 0 and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].y + bh > TINGGI_WINDOW and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].x < 0 and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].x + bw > LEBAR_WINDOW and blast in blasts:
                blasts.remove(blast)

            # Untuk mengecek apakah ada asteroid yang terkena tembakan pesawat
            # Jika tembakannya kena asteroid, hapus tembakan yang terkena tersebut dari list
            blast_rect = pygame.Rect(blast_draw_pos.x, blast_draw_pos.y, bw, bh)
            for rock in rocks[:]:
                if blast_rect.colliderect(rock['rect']) and blast in blasts:
                    
                    rotated_rock_surf = pygame.transform.rotate(rock['surf'], rock['rot'])        
                    rw, rh = rotated_rock_surf.get_size()

                    rock_half = objek_asteroid()
                    rock_half['pos'] = Vector2(rock['pos'].x, rock['pos'].y)                    

                    rock['pos'].y -= rh + (rh / 2)
                    rock_half['pos'].y += rh + (rh / 2)                    

                    rock['surf'] = pygame.transform.scale(rotated_rock_surf, (rw - (rw / 4), rh - (rh / 4)))
                    rock_half['surf'] = rock['surf']                    

                    rock['hits'] += 1

                    if rock['hits'] >= NUM_OF_ROCK_SPLIT:
                        rocks.remove(rock)
                    else:
                        rock_half['hits'] = rock['hits']
                        rocks.append(rock_half)
                    
                    blasts.remove(blast)
                    score += 100
                    asteroid_hit_sound.play()

            screen.blit(rotated_blast_surf, blast_draw_pos)

        ## Fungsi yang sama dengan tembakan tapi untuk asteroid
        for rock in rocks[:]:
            rotated_rock_surf = pygame.transform.rotate(rock['surf'], rock['rot'])        
            rw, rh = rotated_rock_surf.get_size()
            rock['rot'] += rock['rot_direction'] * rock['rot_speed'] * time_passed_secs
            rock_draw_pos, r_heading = efek_rotasi(rock, rw, rh)        
            rock['pos'].x += 1.0 * time_passed_secs * rock['speed']        
            rock['rect'] = pygame.Rect(rock_draw_pos.x, rock_draw_pos.y, rw, rh)

            if rock['pos'].y < 0:
                rocks.remove(rock)                
            if rock['pos'].y + rh > TINGGI_WINDOW:
                rocks.remove(rock)
            if rock['pos'].x > LEBAR_WINDOW + LEBAR_ASTEROID:
                rock['pos'].x = -LEBAR_ASTEROID

            screen.blit(rotated_rock_surf, rock_draw_pos)

        ## Update posisi antara asteroid dan pesawat
        if total_time_passed_secs >= 5:
            ship['new'] = False
            total_time_passed_secs = 0            
            
        rotated_ship_surf = pygame.transform.rotate(ship['surf'], ship['rot'])        
        sw, sh = rotated_ship_surf.get_size()
        
        # Ubah posisi peswat secara real time
        ship['rot'] += rot_direction * ship['rot_speed'] * time_passed_secs
        
        ship_draw_pos, s_heading = efek_rotasi(ship, sw, sh)
        s_heading *= mov_direction        
        ship['pos'] += s_heading * time_passed_secs * ship['speed']

        # Mencegah pesawat keluar dari batas jendela
        if ship['pos'].y < sh:
            ship['pos'].y = sh
        if ship['pos'].y + sh > TINGGI_WINDOW:
            ship['pos'].y = TINGGI_WINDOW - sh
        if ship['pos'].x < sw:
            ship['pos'].x = sw
        if ship['pos'].x + sw > LEBAR_WINDOW:
            ship['pos'].x = LEBAR_WINDOW - sw

        # Untuk mengecek apakah pesawat terbentur ke asteroid
        ship_rect = pygame.Rect(ship_draw_pos.x, ship_draw_pos.y, sw, sh)
        for rock in rocks[:]:
            if ship_rect.colliderect(rock['rect']) and not ship['new']:
                total_time_passed_secs = 0
                num_of_lives -= 1
                ship = objek_pesawat()
                player_collision_sound.play()

        # 5 detik pertama pesawat akan berkedip 
        if ship['new']:
            if total_time_passed_secs > 0.5 and total_time_passed_secs < 1:
                rotated_ship_surf.fill(HITAM)
            if total_time_passed_secs > 1.5 and total_time_passed_secs < 2:
                rotated_ship_surf.fill(HITAM)
            if total_time_passed_secs > 2.5 and total_time_passed_secs < 3:
                rotated_ship_surf.fill(HITAM)
            if total_time_passed_secs > 3.5 and total_time_passed_secs < 4:
                rotated_ship_surf.fill(HITAM)
            if total_time_passed_secs > 4.5 and total_time_passed_secs < 5:
                rotated_ship_surf.fill(HITAM)

        screen.blit(rotated_ship_surf, ship_draw_pos)            

        # Menampilkan skor untuk player
        bikin_text(str(score), score_font, screen, (20, 5), MERAH_MUDA)

        # Menampilkan berapa nyawa lagi yang tersisa
        x = 28
        for i in range(num_of_lives):        
            screen.blit(ship['surf'], (x, 60))
            x += LEBAR_PESAWAT + 10

        # Jika tidak ada nyawa tersisa dan player kalah maka game akan berhenti dan menampilkan game over
        if num_of_lives <= 0:
            running = False
            screen_copy = screen.copy()
            screen_rect = screen.get_rect()
            
            if score > top_score:
                top_score = score
                top_score_rect = text_font.render('New Top Score: %s!' % str(top_score), 1, HIJAU).get_rect()
                bikin_text('New Top Score: %s!' % str(top_score), text_font, screen,
                          (screen_rect.centerx - top_score_rect.width / 2, 100))                
                pygame.display.update()
                pygame.time.wait(4000)

            game_over_rect = font_untuk_title.render('Game Over!', 1, HIJAU).get_rect()
            bikin_text('Game Over!', font_untuk_title, screen_copy,
                      (screen_rect.centerx - game_over_rect.width / 2,
                       screen_rect.centery - game_over_rect.height / 2))
            screen.blit(screen_copy, (0, 0))
            pygame.display.update()
            pygame.time.wait(4000)
                
        pygame.display.update()
        
    main()

top_score = 0
if __name__ == '__main__':
    main()