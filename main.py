import pygame
import sys
from player import Player
from pytmx.util_pygame import load_pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale(surf, (36, 36))
        self.rect = self.image.get_rect(topleft=pos)


class Game:

    def __init__(self, size):
        pygame.init()
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.sprite_group = pygame.sprite.Group()
        self.clock = pygame.time.Clock()

    def load_level(self, name):
        tmx_data = load_pygame(name)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 36, y * 36)
                    Tile(pos, surf, self.sprite_group)
        self.player = Player(144, 144, self.sprite_group, self.screen)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill('black')
        self.sprite_group.draw(self.screen)
        self.player.update()
        pygame.display.update()

    def main(self):
        self.load_level("data/levels/level_0.tmx")

        while True:
            self.clock.tick(60)
            self.update()
