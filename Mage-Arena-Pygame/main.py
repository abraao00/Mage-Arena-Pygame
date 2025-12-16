import pygame
import sys
import random
pygame.init()


WIDTH, HEIGHT = 600, 700
ROWS, COLS = 6, 6
TILE = WIDTH // COLS


UI_HEIGHT = 100
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (80,80,80)
YELLOW = (230,230,0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mage Arena")
clock = pygame.time.Clock()
title_font = pygame.font.Font('font/Title.ttf', 50)
big_font = pygame.font.Font('font/Pixeltype.ttf', 50)
small_font = pygame.font.Font('font/Pixeltype.ttf', 25)

ui = pygame.Surface((WIDTH, UI_HEIGHT))
#------------SPRITES------------------
def load(sprite):
    img = pygame.image.load(sprite).convert_alpha()
    return pygame.transform.scale(img, (TILE,TILE))

mage = {
    'down' : [
        load('assets/character/mage/frente1.png'),
        load('assets/character/mage/frente2.png') ],
    'up' : [
        load('assets/character/mage/atras1.png'),
        load('assets/character/mage/atras2.png') ],
    'right' : [
        load('assets/character/mage/direita1.png'),
        load('assets/character/mage/direita2.png') ],
    'left' : [
        load('assets/character/mage/esquerda1.png'),
        load('assets/character/mage/esquerda2.png') ]
}

fireball = {
    'down' : [
        load('assets/projectile/fire_down1.png'),
        load('assets/projectile/fire_down2.png')],
    'up' : [
        load('assets/projectile/fire_up1.png'),
        load('assets/projectile/fire_up2.png')],
    'right' : [
        load('assets/projectile/fire_right1.png'),
        load('assets/projectile/fire_right2.png')],
    'left' : [
        load('assets/projectile/fire_left1.png'),
        load('assets/projectile/fire_left2.png')],
}
ghost = {
    'down' : [
        load('assets/character/ghost/frente1.png'),
        load('assets/character/ghost/frente2.png')],
    'up' : [
        load('assets/character/ghost/atras1.png'),
        load('assets/character/ghost/atras2.png')],
    'right' : [
        load('assets/character/ghost/direita1.png'),
        load('assets/character/ghost/direita2.png')],
    'left' : [
        load('assets/character/ghost/esquerda1.png'),
        load('assets/character/ghost/esquerda2.png')],
}

menu_bg = pygame.image.load("assets/Menu.png").convert()

rock = pygame.image.load('assets/grid.png').convert()
rock = pygame.transform.scale(rock, (TILE,TILE))

potion_img = pygame.image.load("assets/potion.png").convert_alpha()
potion_img = pygame.transform.scale(potion_img, (40, 40))
#============================CLASSES=======================
class Game:
    def __init__(self):
        self.turn = 1
        self.turn_state = "player_move"
        self.phase_index = 0

        self.turn_order = [
            "player_move",
            "player_attack",
            "enemy_attack",
            "enemy_move",
            "enemy_prep",
        ]
        self.messages = []

        self.enemies_killed = 0


    def next_phase(self):
        self.phase_index += 1
        if self.phase_index >= len(self.turn_order):
            self.phase_index = 0
            self.turn += 1
        self.turn_state = self.turn_order[self.phase_index]

    def add_message(self, text):
        self.messages.insert(0,text)
        if len(self.messages) > 3:
            self.messages.pop()

#======================================================
class Player:
    def __init__(self, row, col, sprites):
        self.max_hp = 3
        self.hp = 3
        self.row = row
        self.col = col
        self.past_x = col
        self.past_y = row
        self.dir = "down"
        self.selected = False
        self.valid_moves = []
        self.valid_attacks = []
        self.sprites = sprites

        self.hit_timer = 0

    def get_valid_attacks(self):
        attacks = []
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        for dr, dc in directions:
            nr = self.row + dr
            nc = self.col + dc
            # OOB
            if (0 <= nr < ROWS and 0 <= nc < COLS):
                attacks.append((nr,nc))
        return attacks

    def get_valid_moves(self, enemies):
        moves = []
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        for dr, dc in directions:
            nr = self.row + dr
            nc = self.col + dc
            # OOB
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            # ocupied
            blocked = False
            for e in enemies:
                if e.row == nr and e.col == nc:
                    blocked = True
                    break
            if blocked:
                continue
            moves.append((nr, nc))
        return moves

    def attack(self, arow, acol):
        global projectile
        if projectile is not None:
            return
        
        if arow == -1: self.dir = "up"
        elif arow == 1: self.dir = "down"
        elif acol == -1: self.dir = "left"
        elif acol == 1: self.dir     = "right"

        projectile = {
        "x": self.col,
        "y": self.row,
        "dir": self.dir,
        "speed": 0.20
    }

    def draw_player(self, surf):
        if self.hit_timer > 0:
            if (self.hit_timer // 3) % 2 == 0:
                self.hit_timer -= 1
                return
            self.hit_timer -= 1

        frame = (pygame.time.get_ticks() // 300) % 2
        current = mage[self.dir][frame]

        if self.past_x < self.col: self.past_x += 0.25
        if self.past_x > self.col: self.past_x -= 0.25 
        if self.past_y < self.row: self.past_y += 0.25
        if self.past_y > self.row: self.past_y -= 0.25

        frame = (pygame.time.get_ticks() // 300) % 2
        img = self.sprites[self.dir][frame]
        surf.blit(img, (self.past_x * TILE, self.past_y * TILE))
        #hp
        bar_w = TILE - 10
        bar_h = 6
        bar_x = self.past_x * TILE + 5
        bar_y = self.past_y * TILE + 4
        pygame.draw.rect(surf, (0, 50, 0), (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (0,255,0), (bar_x, bar_y, bar_w * hp_ratio, bar_h))

    def move(self, dr, dc, enemies):
        new_r = self.row + dr
        new_c = self.col + dc
        
        if not (0 <= new_r < ROWS and 0 <= new_c < COLS):
            return
        
        for e in enemies:
            if e.row == new_r and e.col == new_c:
                return
        
        if dr == -1: self.dir = "up"
        elif dr == 1: self.dir = "down"
        elif dc == -1: self.dir = "left"
        elif dc == 1: self.dir = "right"

        self.row = new_r
        self.col = new_c

#===============================================================
class Enemy:
    def __init__(self, row, col, sprites, spawning=False):
        self.row = row
        self.col = col
        self.sprites = sprites

        self.past_x = col
        self.past_y = row
        self.dir = "down"

        self.prep_tile = None # (x,y)
        self.has_prepared = False

        self.max_hp = 2
        self.hp = 2

        self.spawning = spawning
        self.spawn_timer = 1 if spawning else 0
    # -------------------------------------
    def update_anim(self):
        if self.past_x < self.col: self.past_x += 0.25
        if self.past_x > self.col: self.past_x -= 0.25
        if self.past_y < self.row: self.past_y += 0.25
        if self.past_y > self.row: self.past_y -= 0.25
    # -------------------------------------
    def draw(self, surf):
        frame = (pygame.time.get_ticks() // 300) % 2
        img = self.sprites[self.dir][frame]
        if self.spawning:
            img = img.copy()
            img.set_alpha(120)
        
        surf.blit(img, (self.past_x * TILE, self.past_y * TILE))
        #atack prep
        if self.has_prepared and self.prep_tile:
            pr, pc = self.prep_tile
            arrow = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            arrow.fill((255, 26, 26, 120))
            surf.blit(arrow, (pc*TILE, pr*TILE))
        #hp
        bar_w = TILE - 10
        bar_h = 6
        bar_x = self.past_x * TILE + 5
        bar_y = self.past_y * TILE + 4
        pygame.draw.rect(surf, (50, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (255, 0, 0), (bar_x, bar_y, bar_w * hp_ratio, bar_h))
    # -------------------------------------
    def is_adjacent(self, player):
        directions = [(1, 0),(-1, 0),(0, 1),(0, -1)]
        for dr, dc in directions:
            nr = self.row + dr
            nc = self.col + dc
            if nr == player.row and nc == player.col:
                return True
        return False
    # -------------------------------------
    def move_towards_player(self, player, enemies):
        if self.spawning:
            return
        if self.is_adjacent(player):
            return
        dr = player.row - self.row
        dc = player.col - self.col

        def can_go(r, c):
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return False
            return not tile_occupied(r, c, player, enemies)

        # try bigger axis
        primary_vertical = abs(dr) > abs(dc)
        targets = []
        if primary_vertical:
            step_r = 1 if dr > 0 else -1
            targets.append((self.row + step_r, self.col))
            step_c = 1 if dc > 0 else -1
            targets.append((self.row, self.col + step_c))
        else:
            step_c = 1 if dc > 0 else -1
            targets.append((self.row, self.col + step_c))
            step_r = 1 if dr > 0 else -1
            targets.append((self.row + step_r, self.col))

        for nr, nc in targets:
            if can_go(nr, nc):
                if nr < self.row: self.dir = "up"
                elif nr > self.row: self.dir = "down"
                elif nc < self.col: self.dir = "left"
                elif nc > self.col: self.dir = "right"

                self.row, self.col = nr, nc
                break
    # -------------------------------------
    def prep_attack(self, player):
        if self.spawning:
            return

        if not self.is_adjacent(player):
            self.prep_tile = None
            self.has_prepared = False
            return

        self.prep_tile = (player.row, player.col)
        self.has_prepared = True
        dr = player.row - self.row
        dc = player.col - self.col

        if abs(dr) > abs(dc):
            if dr < 0: self.dir = "up"
            else: self.dir = "down"
        else: 
            if dc < 0: self.dir = "left"
            else: self.dir = "right"
    # -------------------------------------
    def attack(self, player):
        if self.spawning:
            return
        if not self.has_prepared:
            return
        if self.prep_tile == (player.row, player.col):
            player.hp -= 1
            player.hit_timer = 20
            g.add_message("Took a hit! -1HP ")
        self.prep_tile = None
        self.has_prepared = False

#===============================================================================
def tile_occupied(r, c, player, enemies):
    if (player.row == r and player.col == c):
        return True
    for e in enemies:
        if e.row == r and e.col == c:
            return True
    return False

def random_free_tile(player, enemies):
    free_tiles = []
    for r in range(ROWS):
        for c in range(COLS):
            if not tile_occupied(r, c, player, enemies):
                free_tiles.append((r, c))
    if not free_tiles:
        return None
    return random.choice(free_tiles)

def spawn_enemy(player, enemies):
    pos = random_free_tile(player, enemies)
    if pos is None:
        return
    r, c = pos
    enemies.append(Enemy(r, c, ghost, spawning = True))

def control_enemy_population(player, enemies, turn):
    desired = 4 + (turn // 6)
    desired = min(desired, 6)

    missing = desired - len(enemies)

    if missing <= 0:
        return

    spawn_enemy(player, enemies)


#-------------------------Draw----------------------------
def draw_ui():
    global skip_button, heal_button
    ui.fill((7, 5, 27))
 
    skip = big_font.render("SKIP TURN", False, WHITE)
    skip_rect = skip.get_rect()
    #potion
    heal_button = pygame.Rect(370, 15, 42, 42)
    pygame.draw.rect(ui, BLACK, heal_button)
    pygame.draw.rect(ui, GREY, heal_button, 3)
    ui.blit(potion_img,(370,15))
    #skip
    skip_button = pygame.Rect(420,15,skip_rect.width + 20,skip_rect.height + 10)
    pygame.draw.rect(ui, BLACK, skip_button)
    pygame.draw.rect(ui, GREY, skip_button, 3)
    skip_rect.center = (skip_button.centerx, skip_button.centery +4)
    ui.blit(skip , skip_rect)
    #turn
    turn_counter = small_font.render(f"Round: {g.turn}", False, WHITE)
    ui.blit(turn_counter,(480, 65))
    #message
    msg_y = 35
    for msg in g.messages:
        txt = small_font.render(msg, False, (200,200,200))
        ui.blit(txt, (15, msg_y))
        msg_y += 20
    
    phase = small_font.render(f"TURN: {g.turn_state.replace('_',' ').upper()}", True, WHITE)
    ui.blit(phase, (15, 10))

    screen.blit(ui,(0,HEIGHT - UI_HEIGHT))

def draw_help():
    global back_button
    screen.blit(menu_bg, (0, 0))

    title = title_font.render("HOW TO PLAY", True, (45, 32, 67))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 90)))
    card_w, card_h = 420, 260
    card_x = WIDTH // 2 - card_w // 2
    card_y = HEIGHT // 2 - card_h // 2
    card = pygame.Rect(card_x, card_y, card_w, card_h)
    pygame.draw.rect(screen, (20, 20, 20), card)
    pygame.draw.rect(screen, GREY, card, 3)

    instructions = [
        " Click on your character to select",
        " Click green tiles to MOVE",
        " Click your character again to ATTACK",
        " Click orange tiles to shoot fire",
        "======================================",
        " Enemies show red tiles before attacking",
        " Defeat enemies to survive more rounds",
        " Use potions to heal (attack turn)",
    ]
    y = card_y + 25
    for line in instructions:
        txt = small_font.render(line, True, WHITE)
        screen.blit(txt, (card_x + 20, y))
        y += 28
    back_button = pygame.Rect(WIDTH//2 - 90, card.bottom + 20, 180, 45)
    pygame.draw.rect(screen, (20, 20, 20), back_button)
    pygame.draw.rect(screen, GREY, back_button, 3)
    back_txt = big_font.render("BACK", True, WHITE)
    back_rect = back_txt.get_rect(center=back_button.center)
    back_rect.y += 4
    screen.blit(back_txt, back_rect)


def draw_gameover():
    global menu_button
    screen.blit(menu_bg, (0, 0))
    title = title_font.render("GAME OVER", True, (45, 32, 67))
    title_rect = title.get_rect(center=(WIDTH // 2, 90))
    screen.blit(title, title_rect)
    score_w, score_h = 200, 100
    score_x = WIDTH - score_w - 40
    score_y = HEIGHT // 2 - score_h // 2
    score = pygame.Rect(score_x,score_y,score_w,score_h)
    pygame.draw.rect(screen, (20, 20, 20), score)
    pygame.draw.rect(screen, GREY, score, 3)

    score_title = small_font.render("SCORE", True, (200, 200, 200))
    score_title_rect = score_title.get_rect(center=(score.centerx, score.y + 20))
    screen.blit(score_title, score_title_rect)

    kills_txt = small_font.render(f"Enemies defeated: {g.enemies_killed}", True, WHITE)
    kills_rect = kills_txt.get_rect(center=(score.centerx, score.y + 55))
    screen.blit(kills_txt, kills_rect)
    rounds_txt = small_font.render(f"Rounds survived: {g.turn}", True, WHITE)
    rounds_rect = rounds_txt.get_rect(center=(score.centerx, score.y + 80))
    screen.blit(rounds_txt, rounds_rect)

    btn_w, btn_h = 180, 50
    btn_x = WIDTH - btn_w - 50
    btn_y = score.bottom + 20
    menu_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, (20, 20, 20), menu_button)
    pygame.draw.rect(screen, GREY, menu_button, 3)
    btn_txt = big_font.render("RESTART", True, WHITE)
    btn_rect = btn_txt.get_rect(center=menu_button.center)
    btn_rect.y += 4
    screen.blit(btn_txt, btn_rect)

    credit = small_font.render("Created by: Eduardo Zanchet", True, (180,180,180))
    credit_rect = credit.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(credit, credit_rect)


def draw_menu():
    global start_button, help_button
    screen.blit(menu_bg, (0, 0))
    title = title_font.render("MAGE ARENA", True, (45, 32, 67))
    title_rect = title.get_rect(center=(WIDTH // 2, 90))
    screen.blit(title, title_rect)
    btn_w, btn_h = 180, 50
    btn_x = WIDTH - btn_w - 40
    btn_y = HEIGHT // 2 - btn_h // 2
    start_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, (20, 20, 20), start_button)
    pygame.draw.rect(screen, GREY, start_button, 3)
    start_txt = big_font.render("START", True, WHITE)
    start_rect = start_txt.get_rect(center=start_button.center)
    start_rect.y += 4
    screen.blit(start_txt, start_rect)
    
    help_button = pygame.Rect(btn_x, btn_y + 70, btn_w, btn_h)
    pygame.draw.rect(screen, (20, 20, 20), help_button)
    pygame.draw.rect(screen, GREY, help_button, 3)

    help_txt = big_font.render("HELP", True, WHITE)
    help_rect = help_txt.get_rect(center=help_button.center)
    help_rect.y += 4
    screen.blit(help_txt, help_rect)

    credit = small_font.render("Created by: Eduardo Zanchet", True, (180,180,180))
    credit_rect = credit.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(credit, credit_rect)



def draw_projectile():
    if projectile is None:
        return
    frame = (pygame.time.get_ticks() // 150) % 2
    img = fireball[projectile["dir"]][frame]
    px = projectile["x"] * TILE
    py = projectile["y"] * TILE
    screen.blit(img, (px,py))



def update_projectile(enemies):
    global projectile
    if projectile is None:
        return
    if projectile["dir"] == "up":
        projectile["y"] -= projectile["speed"]
    elif projectile["dir"] == "down":
        projectile["y"] += projectile["speed"]
    elif projectile["dir"] == "left":
        projectile["x"] -= projectile["speed"]
    elif projectile["dir"] == "right":
        projectile["x"] += projectile["speed"]

    tile_r = int(projectile["y"])
    tile_c = int(projectile["x"])
    # out of bounds
    if not (0 <= tile_r < ROWS and 0 <= tile_c < COLS):
        projectile = None
        return
    # hit
    for e in enemies:
        if e.row == tile_r and e.col == tile_c:
            e.hp -= 1    
            projectile = None
            return

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            x = c * TILE
            y = r * TILE
            screen.blit(rock, (c*TILE, r*TILE))


def start_game():
    global game_stage, g, enemies, projectile, player

    game_stage = "playing"
    g = Game()
    projectile = None
    enemies = []
    enemies.clear()
    player = Player(0,0,mage)
    for _ in range(4):
        spawn_enemy(player, enemies)

    

# ==============================LOOP=================================

game_stage = "menu"
g = Game()
projectile = None
enemies = []
enemies.clear()
#player = Player(0,0,mage)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_stage == "menu":
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if start_button.collidepoint(mx,my):
                    start_game()
                if help_button.collidepoint(mx, my):
                    game_stage = "help"
            continue
        
        if game_stage == "game_over":
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if menu_button.collidepoint(mx,my):
                    game_stage = "menu"
            continue

        if game_stage == "help":
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if back_button.collidepoint(mx, my):
                    game_stage = "menu"
            continue
                
        #----------------------CLICKS---------------
        if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                ui_y = my - (HEIGHT - UI_HEIGHT)
            #------------------UI INTERACTION---------------
                if my >= HEIGHT - UI_HEIGHT:
                    if skip_button.collidepoint(mx,ui_y):
                        if g.turn_state in ("player_move", "player_attack"):
                            g.add_message("Turn Skipped!")
                            g.next_phase()
                            player.selected = False
                            player.valid_moves = []
                            player.valid_attacks = []


                    if heal_button.collidepoint(mx, ui_y):
                        if g.turn_state == "player_attack":
                            if player.hp < player.max_hp:
                                player.hp += 1
                                g.next_phase()
                                player.selected = False
                                player.valid_attacks = []
                                g.add_message("Recovered +1HP!")
                                
                            else:   
                                g.add_message("Already full HP.")
                                pass
                        else:
                            g.add_message("Can't heal on move turn.")
                            pass
                #--------------------TURNS----------------
                # =============MOVE============
                if g.turn_state == "player_move":
                    mrow = my // TILE
                    mcol = mx // TILE

                    if (mrow, mcol) == (player.row, player.col):
                        player.selected = True
                        player.valid_moves = player.get_valid_moves(enemies)

                    elif player.selected and (mrow, mcol) in player.valid_moves:
                        player.move(mrow - player.row, mcol - player.col, enemies)
                        player.selected = False
                        player.valid_moves = []
                        g.next_phase()

                    else:
                        player.selected = False
                        player.valid_moves = []
                #================ATTACK=================
                elif g.turn_state == "player_attack":
                    mrow = my // TILE
                    mcol = mx // TILE

                    if (mrow, mcol) == (player.row, player.col):
                        player.selected = True
                        player.valid_attacks = player.get_valid_attacks()

                    elif player.selected and (mrow, mcol) in player.valid_attacks:
                        player.attack(mrow - player.row, mcol - player.col)
                        player.selected = False
                        player.valid_attacks = []
                        g.next_phase()
                    else:
                        player.selected = False
                        player.valid_attacks = []   

    update_projectile(enemies)
    if game_stage == "playing":
        to_remove = []
        for en in enemies:
            if en.hp <= 0:
                g.enemies_killed += 1
                to_remove.append(en)
                g.add_message("One enemy was defeated!")


        for dead in to_remove:
            dead.has_prepared = False
            dead.prep_tile = None
            enemies.remove(dead)

        if projectile is not None:
            pass
        else:
            #================ENEMY-===========
            if g.turn_state == "enemy_move":
                for en in enemies:
                    if en.spawning:
                        en.spawn_timer -= 1
                        if en.spawn_timer <= 0:
                            en.spawning = False

                for en in enemies:  
                    en.move_towards_player(player, enemies)
                g.next_phase()

            elif g.turn_state == "enemy_prep":
                for en in enemies:
                    en.prep_attack(player)

                
                            
                control_enemy_population(player, enemies, g.turn)
                g.next_phase()

            elif g.turn_state == "enemy_attack":
                for en in enemies:
                    en.attack(player)

                g.next_phase()
                
            
    # -----------------------------
    # DRAW
    # ----------------------------- 
    
    screen.fill(BLACK)

    if game_stage == "menu":
        draw_menu()
    
    elif game_stage == "playing":
        draw_grid()
        draw_ui()   
        
        for en in enemies:
            en.update_anim()
            en.draw(screen)
        if player.selected:
            for r, c in player.valid_moves:
                highlight = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                highlight.fill((0,255,0,50))
                screen.blit(highlight, (c*TILE, r*TILE))
            for r, c in player.valid_attacks:
                highlight = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                highlight.fill((255, 117, 0,70))
                screen.blit(highlight, (c*TILE, r*TILE))
            pygame.draw.rect(screen, YELLOW, (player.col*TILE, player.row*TILE, TILE, TILE), 4)

        draw_projectile()
        player.draw_player(screen)


    elif game_stage == "game_over":
        draw_gameover()
    
    elif game_stage == "help":
        draw_help()

    if game_stage == "playing" and player.hp <= 0:
        game_stage = "game_over"

    pygame.display.update()
    clock.tick(60)