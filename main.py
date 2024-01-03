import pygame
import sys
from player import Player, load_anim
from pytmx.util_pygame import load_pygame
ANIM = pygame.USEREVENT + 1


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale(surf, (36, 36))
        self.rect = self.image.get_rect(topleft=pos)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.frames = load_anim("coin", 6, (32, 32))
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Game:
    def __init__(self, size):
        pygame.init()
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.ground_group = pygame.sprite.Group()
        self.decorate_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.score = 0
        pygame.time.set_timer(ANIM, 200)

    def load_level(self, name):
        tmx_data = load_pygame(name)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 36, y * 36)
                    if layer.name == "ground":
                        Tile(pos, surf, self.ground_group)
                    elif layer.name == "ch":
                        Tile(pos, surf, self.decorate_group)
                    elif layer.name == "coins":
                        Coin(pos, self.coin_group)

        self.player = Player(144, 144, self.ground_group, self.screen)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == ANIM:
                for coin in self.coin_group:
                    coin.update()
                self.player.anim()

        if pygame.sprite.spritecollide(self.player, self.coin_group, True):
            self.score += 1
            print(self.score)

        self.screen.fill('black')
        self.ground_group.draw(self.screen)
        self.decorate_group.draw(self.screen)
        self.coin_group.draw(self.screen)
        self.player.update()
        pygame.display.update()

    def main(self):
        self.load_level("data/levels/level_0.tmx")

        while True:
            self.clock.tick(60)
            self.update()
