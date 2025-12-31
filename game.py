import sys
import pygame

class Game:
  def __init__(self):
    # Initialize the pygame library
    pygame.init()
    # Set the window name
    pygame.display.set_caption("Ninja Game")
    # Set output window resolution
    self.screen = pygame.display.set_mode((640, 480))

    self.clock = pygame.time.Clock()

    # Load the cloud image and key out black background
    self.img = pygame.image.load("data/images/clouds/cloud_1.png")
    self.img.set_colorkey((0, 0, 0)) # RGB for pure black

    self.img_pos = [160, 260] # x and y coordinates
    self.movement = [False, False]

    # Drawing a static rectangle to demonstrate collision logic
    self.collision_area = pygame.Rect(50, 50, 300, 50)

  def run(self):
    while True:
      # Clearing the screen
      self.screen.fill((14, 219, 248)) # RGB for sky blue

      # Calculate y-axis of movement
      self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5

      # Drawing a static rectangle that changes shades whenever it registers a collision
      img_r = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())
      # Alternative formatting: pygame.Rect(*self.img_pos, *self.img.get_size()) which "splats" it to (a, b, c, d)
      if img_r.colliderect(self.collision_area): # In this frame, the two rectangles are overlapping
        pygame.draw.rect(self.screen, (0, 100, 255), self.collision_area)
      else:
        pygame.draw.rect(self.screen, (0, 100, 155), self.collision_area)

      # Rendering the moveable sprite
      self.screen.blit(self.img, self.img_pos)

      # Event-handling logic
      for event in pygame.event.get():
        # Quitting the game
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if event.type == pygame.KEYDOWN: # Pressing a key
          if event.key == pygame.K_UP:
            self.movement[0] = True
          if event.key == pygame.K_DOWN:
            self.movement[1] = True
        if event.type == pygame.KEYUP: # Releasing a key
          if event.key == pygame.K_UP:
            self.movement[0] = False
          if event.key == pygame.K_DOWN:
            self.movement[1] = False

      pygame.display.update()
      self.clock.tick(60) # ensures 60 FPS

Game().run()
