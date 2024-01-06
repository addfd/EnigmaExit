import pygame
from random import randint


class Weather:
    def __init__(self, group, screen, width, height):
        self.group = group
        self.screen = screen
        self.width = width
        self.height = height
        self.timer = 0

    def create_particles(self):
        for _ in range(20):
            Rain((randint(0, self.width), randint(-40, -10)), self.screen, self.height, self.group)

    def update(self):
        self.timer += 1
        if self.timer >= 10:
            self.create_particles()
            self.timer = 0


class Rain(pygame.sprite.Sprite):
    def __init__(self, pos, screen, height, group):
        super().__init__(group)
        self.screen = screen
        self.image = pygame.Surface([1, 5])
        self.rect = self.image.get_rect()
        self.height = height

        self.velocity = [0, 1]
        self.rect.x, self.rect.y = pos

        self.gravity = 0.05

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.y += self.velocity[1]
        pygame.draw.line(self.screen, (0, 150, 255), (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 5))
        if self.rect.y > self.height:
            self.kill()
