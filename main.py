import pygame
import sys
from pytmx.util_pygame import load_pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Game:

    def __init__(self, size):
        pygame.init()
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.sprite_group = pygame.sprite.Group()

    def load_level(self, name):
        tmx_data = load_pygame(name)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 12, y * 12)
                    Tile(pos, surf, self.sprite_group)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill('black')
        self.sprite_group.draw(self.screen)
        pygame.display.update()
