import pygame


class Player():
    def __init__(self, x, y, world, screen):
        self.screen = screen

        self.world = world
        self.image = pygame.image.load('data/res/player/idle/0.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (16, 32))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.counter = 0

        self.jump_force = 10
        self.speed = 3
        self.in_air = False

    def update(self):
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
            self.vel_y = -15
            self.jumped = True
        if key[pygame.K_UP] == False:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
            self.counter = 0

        # gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # collision
        self.in_air = True
        for tile in self.world:
            tile = tile.rect
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile.bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

        self.screen.blit(self.image, self.rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2)
