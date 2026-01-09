import sys
import pygame

from scripts.utils import load_images
from scripts.tilemaps import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()

        # Import mapping assets
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
        }
        self.tilemap = Tilemap(self, tile_size=16)

        # Need a method for moving the camera around in x and y axes
        self.movement = [False, False, False, False]
        self.scroll = [0, 0]

        # Iterable list of tiles we can cycle through and place with mouseclick
        self.tile_list = list(self.assets)
        self.tile_group = 0 # Index for the list
        self.tile_variant = 0 # For tiles that have alternative versions
        self.clicking = False
        self.right_clicking = False
        self.shift = False

    def run(self):
        while True:
            # Black background
            self.display.fill((0, 0, 0))

            # Show the current tile selected
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)
            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                # Quitting the level editor
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Laying down currently selected tile when we click down on the mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift: # If holding shift, using the variant tiles instead
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]]) # Number of variant tiles as the limit
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                # Moving around in the level editor with the arrow keys
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key ==  pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # scaling up the display to the screen size
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0,))

            pygame.display.update()
            self.clock.tick(60)  # ensures 60 FPS

Editor().run()
