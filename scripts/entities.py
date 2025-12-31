import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos) # using a list instead of a tuple for some reason
        self.size = size
        self.velocity = [0, 0] # rate of change in the X and Y axis

    def update(self, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0] # update the x position
        self.pos[1] + frame_movement[1] # update the y position

    def render(self, surface):
        surface.blit(self.game.assets['player'], self.pos)
