import pygame


def load_anim(type, count, size):
    anim = []
    for name in range(count):
        anim.append(pygame.transform.scale(pygame.image.load(f'data/res/{type}/{name}.png').convert_alpha(), size))
    return anim


class Player():
    def __init__(self, pos, world, screen):
        self.screen = screen

        self.hit_frames = load_anim("player/hit", 2, (21, 48))
        self.state = {"idle": load_anim("player/idle", 6, (24, 48)), "run": load_anim("player/run", 8, (27, 48)),
                      "jump": load_anim("player/jump", 4, (27, 48)), "fall": load_anim("player/fall", 4, (36, 45)),
                      "death": load_anim("player/death", 12, (24, 48))}

        self.cur_frame = 0
        self.cur_state = "idle"
        self.image = self.state[self.cur_state][self.cur_frame]

        self.world = world

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0

        self.jump_force = 16
        self.speed = 3
        self.time_no_hit = 120  # ~2 c
        self.timehit = 0

        self.life = 3
        self.life_sprite = [pygame.transform.scale(pygame.image.load('data/gui/life/0.png').convert_alpha(), (10, 9)),
                            pygame.transform.scale(pygame.image.load('data/gui/life/1.png').convert_alpha(), (10, 9))]

        self.in_air = False
        self.move = False
        self.jumped = False
        self.flip = False
        self.hit = False
        self.death = False
        self.restart = False

    def update(self):
        if not self.death:
            dx = 0
            dy = 0

            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                self.vel_y = -self.jump_force
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= self.speed
                self.move = True
                self.flip = True
            if key[pygame.K_RIGHT]:
                dx += self.speed
                self.move = True
                self.flip = False
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.move = False

            # gravity
            self.vel_y += 1
            if self.vel_y > 8:
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

        # pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2)

        if self.hit:
            self.render_life()
            self.timehit += 1
            if self.timehit >= self.time_no_hit:
                self.hit = False
                self.timehit = 0
                if self.life == 0:
                    self.death = True
                    self.cur_state = "death"
                    self.cur_frame = -1

    def anim(self):
        if self.death:
            self.cur_frame += 1
            self.image = pygame.transform.flip(self.state[self.cur_state][self.cur_frame], self.flip, False)
            if self.cur_frame == 11:
                pygame.time.delay(100)
                self.restart = True
        else:
            if self.in_air and self.jumped:
                self.cur_state = "jump"
            elif self.in_air:
                self.cur_state = "fall"
            elif self.move:
                self.cur_state = "run"
            else:
                self.cur_state = "idle"

            self.cur_frame = (self.cur_frame + 1) % len(self.state[self.cur_state])
            self.image = pygame.transform.flip(self.state[self.cur_state][self.cur_frame], self.flip, False)

    def hiting(self):
        self.hit = True
        self.life -= 1
        self.image = pygame.transform.flip(self.hit_frames[0], self.flip, False)
        pygame.time.delay(100)
        self.image = pygame.transform.flip(self.hit_frames[1], self.flip, False)
        if self.life == 0:
            self.time_no_hit = 40

    def render_life(self):
        pos = self.rect.center
        for i in range(1, 4):
            if i <= self.life:
                self.screen.blit(self.life_sprite[0], (pos[0] - 25 + 11 * i, pos[1] - 40))
            else:
                self.screen.blit(self.life_sprite[1], (pos[0] - 25 + 11 * i, pos[1] - 40))
