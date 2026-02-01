import os
import sys
import math
import pygame
import random

from pygame.mixer_music import set_volume

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemaps import Tilemap
from scripts.clouds import Clouds
from scripts.particles import Particle
from scripts.sparks import Spark

class Game:
    def __init__(self):
        """Initialize the Game!"""
        # Initialize the pygame library
        pygame.init()

        # Set the window name
        pygame.display.set_caption('Ninja Game')

        # Set output window resolution
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        # mass importing the following asset folders
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background' : load_image('background.png'),
            'clouds' : load_images('clouds'),
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=6),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun' : load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        # Importing sound effects
        self.sfx = {
            'jump' : pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash' : pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit' : pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot' : pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience' : pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['jump'].set_volume(0.4)
        self.sfx['dash'].set_volume(0.8)
        self.sfx['hit'].set_volume(0.3)
        self.sfx['shoot'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0

    def load_level(self, map_id):
        """Loading the pre-made levels

        :param map_id : the name of the .json file
        """
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        # Locate the trees on the tilemap from which we can spawn leaves particles
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        # Spawning the player character and enemy sprites
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']  # Player spawning position
                self.player.air_time = 0 # Reset air time on respawn
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        # Projectile system
        self.projectiles = []
        # Particles system
        self.particles = []
        # Effects for getting shot and taking hits
        self.sparks = []
        # Scrolling and camera handling
        self.scroll = [0, 0]
        # Handling player death
        self.dead = 0
        # Level transition
        self.transition = -30


    def run(self):
        # Loading and playing background music
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        # Also play the ambience sound effects
        self.sfx['ambience'].play(-1)

        # CORE GAMEPLAY LOOP
        while True:
            # Clearing the screen
            self.display.fill((0, 0, 0, 0))
            self.display2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            # Move to the next level if we've slain all foes
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

            # Move towards the player at a dynamic rate
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30
            # Fixing subpixel "jitter" during camera motion
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Spawning particles
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    # Any random space within bounds of the rectangle
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # Draw the clouds before the tiles so they're in the background
            self.clouds.update()
            self.clouds.render(self.display2, offset=render_scroll)

            # Rendering the tilemap behind the player
            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                # Calculate the horizontal movement vector and account for physics and collisions
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) # in a platformer you move left to right
                # Rendering the moveable player sprite
                self.player.render(self.display, offset=render_scroll)

            # Updating and drawing any projectiles
            for projectile in self.projectiles.copy(): # [[x, y], direction, timer]
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]): # Projectile strikes solid object
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360: # Timer on projectile passed 6 seconds
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50: # Player is in a vulnerable state
                    # Check whether Player is getting hit by the projectile
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                     math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))

            # Drawing sparks effects
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_silhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0,), (1, 0), (0, -1), (0, 1)]:
                self.display2.blit(display_silhouette, offset)

            # Managing the particles system
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.position[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # Event-handling logic
            for event in pygame.event.get():
                # Quitting the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN: # Pressing a key
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP: # Releasing a key
                    if event.key ==  pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # Shrinking and expanding circle for level transitions
            if self.transition:
                transition_surface = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surface, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surface.set_colorkey((255, 255, 255))
                self.display.blit(transition_surface, (0, 0))

            self.display2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            # scaling up the display to the screen size
            self.screen.blit(pygame.transform.scale(self.display2, self.screen.get_size()), screenshake_offset)

            pygame.display.update()
            self.clock.tick(60)  # ensures 60 FPS

Game().run()
