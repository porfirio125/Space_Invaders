from random import choice, randint
from math import ceil
import pygame
import os

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
SPRINGREEN = (0, 250, 154)



SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600



DIRECTORY = os.getcwd()


FONT = DIRECTORY + "/fonts/space_invaders.ttf"


class Edge(pygame.sprite.Sprite):


    def __init__(self, width, height, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(pygame.sprite.Sprite):


    def __init__(self, color = WHITE, size = 10):
 
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.size = size
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(color)
        self.rect = self.image.get_rect()


class Ship(pygame.sprite.Sprite):

    
    def __init__(self, path, pos_x, pos_y, speed = 5):

        pygame.sprite.Sprite.__init__(self)
        self.__initial_position = (pos_x, pos_y)

        self.__image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.__image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.speed = speed

        self.lifes = 3

        self.__sound_shot = pygame.mixer.Sound(DIRECTORY + "/sounds/shoot.wav")
        self.__ship_explosion = pygame.mixer.Sound(DIRECTORY + "/sounds/shipexplosion.wav")

    def initial_position(self):
  
        self.rect.x = self.__initial_position[0]
        self.rect.y = self.__initial_position[1]

    def die(self):

        self.__ship_explosion.play()
        self.initial_position()
        self.lifes -= 1

    def shoot(self):

        self.__sound_shot.play()
        bullet = Bullet(self.rect.midtop, 1)
        return bullet

    def update(self, *args):


        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            if self.rect.right < (SCREEN_WIDTH - self.speed):
                self.rect.x += self.speed

        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            if self.rect.left > self.speed:
                self.rect.x -= self.speed

    def __str__(self):

        return "Ship in (%s, %s)" % (self.rect.x, self.rect.y)

class Invader(pygame.sprite.Sprite):

    def __init__(self, sprite, pos_x, pos_y, speed = 1):

        pygame.sprite.Sprite.__init__(self)
        self.image = sprite
        self.rect = sprite.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.speed = speed

    def shoot(self):

        bullet = Bullet(self.rect.midtop, -1, speed = 4, color = RED)
        return bullet
    
    def up_speed(self):

        self.speed += 0.5
    
    def down_invader(self):

        self.rect.y += 20

    def update(self, direction):

        self.rect = self.rect.move(self.speed * direction, 0)

    def __str__(self):

        return "Invader in (%s, %s)" % (self.rect.x, self.rect.y)


class Mystery(pygame.sprite.Sprite):


    def __init__(self, sprite, pos_x, pos_y, speed = 2.7):

        pygame.sprite.Sprite.__init__(self)
        self.image = sprite
        self.rect = self.image.get_rect(topleft = (pos_x, pos_y))
        self.speed = speed
    
    def update(self, *args):
        if (self.rect.x >= (SCREEN_WIDTH + 200)):
            self.kill()
        else:
            self.rect = self.rect.move(self.speed, 0)

class Bullet(pygame.sprite.Sprite):


    def __init__(self, pos_xy, direction, color = SPRINGREEN, speed = 8):

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5,10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = pos_xy[0]
        self.rect.y = pos_xy[1]
        self.direction = direction
        self.speed = speed * direction

    def update(self, *args):

        self.rect.y -= self.speed
        if self.rect.bottom <= 0:
            self.kill()


class SpaceInvaders():

    
    def __init__(self):

 
        self.ship_shot = pygame.sprite.GroupSingle()
        self.invader_shot = pygame.sprite.Group()


        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("Space Invaders")

        logo = pygame.image.load(DIRECTORY + "/images/logo.png")
        pygame.display.set_icon(logo)
        self.score = 0
        self.level = 0
        self.speed = 0

        self.font = self.create_font(60)
        self.score_font = self.create_font(15)
        self.explosion_sound = pygame.mixer.Sound(DIRECTORY + "/sounds/invaderkilled.wav")
        

        self.path_image_ship = DIRECTORY + "/images/ship.png"
        background_image = pygame.image.load(DIRECTORY + "/images/back.png")
        explosion_image = pygame.image.load(DIRECTORY + "/images/explosion.png")
        lifes_image = pygame.image.load(DIRECTORY + "/images/heart.png")

        self.ship = pygame.sprite.GroupSingle(
                                Ship(self.path_image_ship, (SCREEN_WIDTH - 50) // 2, 
                                        (SCREEN_HEIGHT - 110)))
        self.ship_sprite = self.ship.sprites()[0]
        mystery_image = pygame.image.load(DIRECTORY + "/images/boss3.png")
        self.mystery_image = pygame.transform.scale(mystery_image, [71, 39])
        self.mystery = pygame.sprite.GroupSingle(
                                Mystery(self.mystery_image, self.random_position(), 15))
        self.background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.lifes_image = pygame.transform.scale(lifes_image, (25, 25))
        self.explosion_image = pygame.transform.scale(explosion_image, (
                                    (SCREEN_WIDTH // 20), (SCREEN_WIDTH // 20)))
        self.clock = pygame.time.Clock()
        self.invaders = pygame.sprite.OrderedUpdates()
        self.invaders_direction = 1
        self.increment_speed = False
        
        self.left_edge = pygame.sprite.GroupSingle(Edge(5, SCREEN_HEIGHT, 0, 0))
        self.right_edge = pygame.sprite.GroupSingle(Edge(5, SCREEN_HEIGHT, 795, 0))
        self.bottom_edge = pygame.sprite.GroupSingle(Edge(SCREEN_WIDTH, 5, 0, 560))
        self.groups = pygame.sprite.Group(self.ship_shot, self.invader_shot, 
                                    self.invaders, self.mystery)

    def random_position(self):
 
        return choice([-1700, -1900, -2200, -2500, -1500])

    def home_screen(self):

        menu = True
        music_menu = pygame.mixer.Sound(DIRECTORY + "/sounds/menu.wav")
        music_menu.play(-1)

        text = self.font.render("SPACE INVADERS", True, GREEN)
        self.font = self.create_font(20)
        command1 = self.font.render(" ENTER : START ", True, WHITE, None)
        command2 = self.font.render("   ESC : OUT      ", True, WHITE, None)
        command1_rect = command1.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        command2_rect = command2.get_rect(center = ((SCREEN_WIDTH + 15) // 2, SCREEN_HEIGHT - 50))
        
        mystery = pygame.image.load(DIRECTORY + "/images/boss1.png")
        mystery = pygame.transform.scale(mystery, [110, 60])
        speed = [-5, 5]
        rect_mystery = mystery.get_rect()

        self.window.fill(BLACK)
        self.window.blit(text, [(SCREEN_WIDTH - 570) // 2, 50])
        self.window.blit(command1, command1_rect)
        self.window.blit(command2, command2_rect)
        pygame.display.update()

        while menu:
   
            if rect_mystery.left < 0 or rect_mystery.right > SCREEN_WIDTH:
                speed[0] = -speed[0]
            if rect_mystery.top < 0 or rect_mystery.bottom > SCREEN_HEIGHT:
                speed[1] = -speed[1]
            
            rect_mystery.x += speed[0]
            rect_mystery.y += speed[1]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    music_menu.stop()
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_game()
                        music_menu.stop()
                        return True

                    if event.key == pygame.K_ESCAPE:
                        music_menu.stop()
                        return False

            self.window.fill(BLACK)
            self.window.blit(mystery, rect_mystery)
            self.window.blit(text, [(SCREEN_WIDTH - 570) // 2, 50])
            self.window.blit(command1, command1_rect)
            self.window.blit(command2, command2_rect)
            self.clock.tick(60)
            pygame.display.update()
    
    def final_screen(self):

        music_menu = pygame.mixer.Sound(DIRECTORY + "/sounds/menu.wav")
        music_menu.play(-1)
        self.game_over_screen()

        self.font50 = self.create_font(50)
        self.font20 = self.create_font(20)

        text1 = self.font50.render("FINAL SCORE: %d" % self.score, True, GOLD)
        text2 = self.font20.render("PRESS ENTER TO TRY AGAIN", True, WHITE)
        text3 = self.font20.render("PRESS ESC TO OUT", True, WHITE)

        text1_rect = text1.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 350))
        text2_rect = text2.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        text3_rect = text3.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))

        self.window.fill(BLACK)
        self.window.blit(text1, text1_rect)
        self.window.blit(text2, text2_rect)
        self.window.blit(text3, text3_rect)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    music_menu.stop()
                    pygame.quit()
                    exit()
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        music_menu.stop()
                        self.level = 0
                        self.speed = 0
                        self.ship = pygame.sprite.GroupSingle(
                                Ship(self.path_image_ship, (SCREEN_WIDTH) // 2, (SCREEN_HEIGHT - 110)))
                        self.ship_sprite = self.ship.sprites()[0]
                        self.start_game()
                        return
						
                    if event.key == pygame.K_ESCAPE:
                        music_menu.stop()
                        pygame.quit()
                        exit()
        
    def level_screen(self):
  
        self.level += 1
        if (self.level > 1 and self.level < 6):
            self.speed += 0.3
        elif (self.level == 1):
            self.speed += 1
        
        font = self.create_font(100)
        text = font.render('LEVEL: ' + str(self.level), True, GOLD)
        self.time = pygame.time.get_ticks()

        while ((pygame.time.get_ticks() - self.time) < 1000):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.window.blit(self.background, [0, 0])
            self.window.blit(text, [(SCREEN_WIDTH - 450) // 2, 220])
            pygame.display.update()
    
    def game_over_screen(self):

        font = self.create_font(100)
        text = font.render('GAME OVER', True, RED)
        time = pygame.time.get_ticks()

        while ((pygame.time.get_ticks() - time) < 1500):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.window.blit(self.background, [0, 0])
            self.window.blit(text, [(SCREEN_WIDTH - 600) // 2, 220])
            pygame.display.update()

    def start_game(self):

        self.groups.add(self.ship)
        self.invaders_direction = 1
        self.blocks = pygame.sprite.Group(self.build_blocks(0),
                                            self.build_blocks(1),
                                            self.build_blocks(2))
        self.invaders.empty()
        self.mystery.empty()
        self.invader_shot.empty()
        self.ship_shot.empty()
        self.level_screen()
        self.create_invaders()
        self.ship_sprite.initial_position()
        self.update()
	
    def build_blocks(self, number):

        aux = pygame.sprite.Group()
        for row in range(4):
            for column in range(10):
                blocker = Block()
                blocker.rect.x = 45 + (300 * number) + (column * blocker.size)
                blocker.rect.y = 400 + (row * blocker.size)
                aux.add(blocker)
        return aux

    def create_invaders(self):

        enemy_types = []

        for i in range(1, 8):
            enemy_types.append(pygame.image.load(DIRECTORY + ("/images/invader%d.png" % (i % 2))))

        x = 25

        for j in range(7):
            y = 60
            for i in range(5):
                sprite = pygame.transform.scale(enemy_types[i], 
                                ((SCREEN_WIDTH // 20), (SCREEN_WIDTH // 20)))
                self.invaders.add(Invader(sprite, x, y, self.speed))
                y += 45
            x += 62

    def showShipLives(self):

        y = 10
        for i in range(self.ship_sprite.lifes):
            self.window.blit(self.lifes_image, (y, 570))
            y += 40

    def enemy_shot(self):

        enemy = [i for i in self.invaders]
        
        for i in range(2):
            invader = choice(enemy)
            self.invader_shot.add(invader.shoot())

    def update(self):

        score = self.score_font.render("SCORE: %d" % self.score, True, WHITE)

        current_time = pygame.time.get_ticks()

        if (current_time % 2000.0 < 20):
            self.enemy_shot()
        
        if ((len(self.mystery) == 0)):
            self.mystery.add(Mystery(self.mystery_image, self.random_position(), 15))

        self.window.blit(self.background, [0, 0])
        self.window.blit(score, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))
        self.groups.draw(self.window)
        self.blocks.draw(self.window)

        self.groups.update(self.invaders_direction)
        self.update_direction()
        self.check_collisions()
        self.showShipLives()

        self.groups = pygame.sprite.Group(self.ship, self.ship_shot, self.invader_shot, self.invaders, 
                                    self.left_edge, self.bottom_edge, self.right_edge, self.mystery)
        self.clock.tick(60)
        pygame.display.update()
    
    def check_collisions(self):

        if pygame.sprite.groupcollide(self.ship_shot, self.invader_shot, True, True):
            self.score += randint(5, 20)
        

        pygame.sprite.groupcollide(self.invader_shot, self.bottom_edge, True, False)

        pygame.sprite.groupcollide(self.invader_shot, self.blocks, True, True)

        pygame.sprite.groupcollide(self.ship_shot, self.blocks, True, True)

        pygame.sprite.groupcollide(self.blocks, self.invaders, True, False)
        

        if pygame.sprite.groupcollide(self.ship, self.invaders, False, False):
            self.ship_sprite.die()
   
        if pygame.sprite.groupcollide(self.mystery, self.ship_shot, True, True):
            self.score += choice([25, 35, 45, 55])
            self.explosion_sound.play()

        for atingidos in pygame.sprite.groupcollide(self.ship_shot, self.invaders, True, True).values():
            for invasor in atingidos:
                self.explosion_sound.play()
                self.window.blit(self.explosion_image, (invasor.rect.x, invasor.rect.y))
                self.score += choice([10, 15, 20, 25, 30, 35, 40])
        

        if (pygame.sprite.groupcollide(self.ship, self.invader_shot, False, True)):
            self.explosion_sound.play()
            self.window.blit(self.explosion_image, (self.ship_sprite.rect.x, self.ship_sprite.rect.y))
            self.ship_sprite.die()

    def update_direction(self):
 
        arr = self.invaders.sprites()
        first = arr[0]
        last = arr[-1]
        
        if ((last.rect.x > (SCREEN_WIDTH - last.rect.width - 10)) or (first.rect.x < 10)):
            self.invaders_direction *= -1
            current_time = pygame.time.get_ticks()
            if (current_time - self.time > (8000 // self.speed)):
                self.down_invader(arr)
    
    def down_invader(self, arr):

        up_speed = (len(self.invaders) <= 8)

        for enemy in arr:
            if up_speed:
                enemy.up_speed()
            enemy.down_invader()

    def create_font(self, size):
        return pygame.font.Font(FONT, size)

    def main(self):


        run = True
        menu = True
        
        while menu:
            command = self.home_screen()

            if not command:
                menu = False
                pygame.quit()
                exit()
        
            while run:
                if self.ship_sprite.lifes <= 0:
                    self.final_screen()
                    self.score = 0
                elif len(self.invaders) == 0:
                    self.start_game()
                else:
                    for event in pygame.event.get():

                        if event.type == pygame.QUIT:
                            run, menu = False, False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                run, menu = False, False
                            if ((event.key == pygame.K_UP or event.key == pygame.K_SPACE) and not self.ship_shot):
                                self.ship_shot.add(self.ship_sprite.shoot())

                    self.update()

if __name__ == "__main__":

    pygame.init()
    pygame.mixer.pre_init(22050, -16, 2, 1024)
    pygame.mixer.init(22050, -16, 2, 1024)
    game = SpaceInvaders()
    game.main()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.quit()