class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = [] # will be relevant in the level editor portion of the class later

        # EXAMPLE: a tilemap containing a row of horizontal grass tiles and the column of vertical stone tiles
        for i in range(10):
            # grass/1.png from grid position (x;y) 3;10 to 12;10
            self.tilemap[str(i + 3) + ';10'] = {'type' : 'grass', 'variant' : 1, 'pos' : (i + 3, 10)}
            # stone/1.png from grid position (x;y) 10;5 to 10;14
            self.tilemap['10;' + str(i + 5)] = {'type' : 'stone', 'variant' : 1, 'pos' : (10, i + 5)}

    def render(self, surface):
        # Render the off-grid "decorative elements" first
        for tile in self.offgrid_tiles:
            surface.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])

        # Drawing the objects that will be used for collision and physics and logic
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))
