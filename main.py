import pygame
import sys
from sound import SoundModule
from player import Player, load_anim
from pytmx.util_pygame import load_pygame
from button import Button
from random import randint

ANIM = pygame.USEREVENT + 1
SONG_ENDED = pygame.USEREVENT + 2


def get_font(size):
    return pygame.font.Font("data/font.ttf", size)


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale(surf, (36, 36))
        self.rect = self.image.get_rect(topleft=pos)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.frames = load_anim("coin", 6, (32, 32))
        self.group = groups
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def update_collide(self, pl):
        if pygame.sprite.collide_rect(self, pl):
            self.kill()
            return True
        return False


class Game:
    def __init__(self, size):
        pygame.init()
        self.width = size[0]
        self.height = size[1]
        self.screen = pygame.display.set_mode((size[0], size[1]))

        self.ground_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.fire_group = pygame.sprite.Group()
        self.key_group = pygame.sprite.Group()
        self.all_sprite = pygame.sprite.Group()
        self.exit = pygame.sprite.Group()

        self.clock = pygame.time.Clock()
        self.coin = 0
        self.levels = {"level_0": "data/levels/level_0.tmx", "level_1": "data/levels/level_1.tmx"}
        self.path_to_save = "data/save/save.txt"
        self.cur_level = None
        self.spawn_pos = None
        self.player = None
        self.key = False
        pygame.time.set_timer(ANIM, 200)

        self.sound = SoundModule(SONG_ENDED)

    def load_level(self, name):
        self.key = False
        self.coin = 0
        tmx_data = load_pygame(name)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 36, y * 36)
                    if layer.name == "ground":
                        Tile(pos, surf, self.ground_group, self.all_sprite)
                    elif layer.name == "ch":
                        Tile(pos, surf, self.all_sprite)
                    elif layer.name == "coins":
                        Coin(pos, self.coin_group, self.all_sprite)
                    elif layer.name == "fire":
                        Tile(pos, surf, self.fire_group, self.all_sprite)
                    elif layer.name == "spawn":
                        self.spawn_pos = pos
                    elif layer.name == "key":
                        Tile(pos, surf, self.key_group, self.all_sprite)
                    elif layer.name == "exit":
                        Tile(pos, surf, self.exit, self.all_sprite)

        self.player = Player(self.spawn_pos, self.ground_group, self.screen)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.del_level()
                    self.main_menu()

            if event.type == ANIM:
                for coin in self.coin_group:
                    coin.update()
                self.player.anim()
            if event.type == SONG_ENDED:
                self.sound.play_next_track()

        for coin in self.coin_group:
            if coin.update_collide(self.player):
                self.coin += 1
                self.sound.coin.play()

        if pygame.sprite.spritecollide(self.player, self.key_group, True):
            self.key = True
        if pygame.sprite.spritecollide(self.player, self.exit, False) and self.key:
            self.del_level()
            self.win_screen()
        if pygame.sprite.spritecollide(self.player, self.fire_group,
                                       False) and not self.player.hit and not self.player.death:
            self.player.hiting()
        if self.player.restart:
            self.del_level()
            self.restart_screen()

        self.screen.fill('black')
        self.all_sprite.draw(self.screen)
        self.player.update()
        pygame.display.update()

    def play(self, level):
        self.load_level(self.levels[level])

        while True:
            self.clock.tick(60)
            self.update()

    def del_level(self):
        for sprite in self.all_sprite:
            sprite.kill()

    def main_menu(self):
        while True:
            # self.screen.blit(BG, (0, 0))
            self.screen.fill('black')
            size_buttons = (184, 56)

            menu_mouse_pos = pygame.mouse.get_pos()

            menu_text = get_font(100).render("ENIGMA EXIT", True, "#b68f40")
            menu_rect = menu_text.get_rect(center=(self.width // 2, 100))

            play_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             size_buttons),
                pos=(self.width // 2, self.height // 2 - self.height * 0.1),
                text_input="Play", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            options_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             size_buttons),
                pos=(self.width // 2, self.height // 2),
                text_input="Options", font=get_font(75), base_color="#d7fcd4",
                hovering_color="White")
            quit_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             size_buttons),
                pos=(self.width // 2, self.height // 2 + self.height * 0.1),
                text_input="Quit", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            self.screen.blit(menu_text, menu_rect)

            for button in [play_button, options_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        self.sound.ui_click.play()
                        self.levels_screen()
                    if options_button.checkForInput(menu_mouse_pos):
                        self.sound.ui_click.play()
                        self.options()
                    if quit_button.checkForInput(menu_mouse_pos):
                        self.sound.ui_click.play()
                        pygame.quit()
                        sys.exit()
                if event.type == SONG_ENDED:
                    self.sound.play_next_track()

            pygame.display.update()

    def options(self):
        ui_volume, music_volume = self.sound.read_settings()
        while True:
            options_mouse_pos = pygame.mouse.get_pos()

            self.screen.fill("black")

            music_volume_text = get_font(60).render("Music volume", True, "white")
            music_volume_rect = music_volume_text.get_rect(center=(self.width // 2 - 200, self.height // 2 - 100))
            self.screen.blit(music_volume_text, music_volume_rect)
            ui_volume_text = get_font(60).render("UI volume", True, "white")
            ui_volume_rect = ui_volume_text.get_rect(center=(self.width // 2 - 220, self.height // 2))
            self.screen.blit(ui_volume_text, ui_volume_rect)

            music_volume_text = get_font(45).render(str(music_volume), True, "white")
            music_volume_rect = music_volume_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
            self.screen.blit(music_volume_text, music_volume_rect)
            ui_volume_text = get_font(45).render(str(ui_volume), True, "white")
            ui_volume_rect = ui_volume_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(ui_volume_text, ui_volume_rect)

            plus_music_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button_small.png").convert_alpha(),
                                             (56, 56)),
                pos=(self.width // 2 + 56, self.height // 2 - 95),
                text_input="+", font=get_font(75), base_color="#d7fcd4", hovering_color="White", shiftx=2, shifty=-8)
            minus_music_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button_small.png").convert_alpha(),
                                             (56, 56)),
                pos=(self.width // 2 - 56, self.height // 2 - 95),
                text_input="-", font=get_font(75), base_color="#d7fcd4", hovering_color="White", shiftx=2, shifty=-8)
            plus_music_button.changeColor(options_mouse_pos)
            minus_music_button.changeColor(options_mouse_pos)
            plus_music_button.update(self.screen)
            minus_music_button.update(self.screen)

            plus_ui_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button_small.png").convert_alpha(),
                                             (56, 56)),
                pos=(self.width // 2 + 56, self.height // 2 + 5),
                text_input="+", font=get_font(75), base_color="#d7fcd4", hovering_color="White", shiftx=2, shifty=-8)
            minus_ui_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button_small.png").convert_alpha(),
                                             (56, 56)),
                pos=(self.width // 2 - 56, self.height // 2 + 5),
                text_input="-", font=get_font(75), base_color="#d7fcd4", hovering_color="White", shiftx=2, shifty=-8)
            plus_ui_button.changeColor(options_mouse_pos)
            minus_ui_button.changeColor(options_mouse_pos)
            plus_ui_button.update(self.screen)
            minus_ui_button.update(self.screen)

            options_back = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (184, 56)),
                pos=(self.width // 2, self.height // 2 + self.height * 0.2),
                text_input="Back", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            options_back.changeColor(options_mouse_pos)
            options_back.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if plus_music_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        if music_volume < 1.0:
                            music_volume = float('{:.1f}'.format(music_volume + 0.1))
                            self.sound.set_volume_music(music_volume)
                    if minus_music_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        if music_volume > 0.0:
                            music_volume = float('{:.1f}'.format(music_volume - 0.1))
                            self.sound.set_volume_music(music_volume)

                    if plus_ui_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        if ui_volume < 1.0:
                            ui_volume = float('{:.1f}'.format(ui_volume + 0.1))
                            self.sound.set_volume_ui(ui_volume)
                    if minus_ui_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        if ui_volume > 0.0:
                            ui_volume = float('{:.1f}'.format(ui_volume - 0.1))
                            self.sound.set_volume_ui(ui_volume)

                    if options_back.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.sound.write_settings([ui_volume, music_volume])
                        self.main_menu()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.sound.write_settings([ui_volume, music_volume])
                        self.main_menu()
                if event.type == SONG_ENDED:
                    self.sound.play_next_track()

            pygame.display.update()

    def restart_screen(self):
        while True:
            options_mouse_pos = pygame.mouse.get_pos()

            self.screen.fill("black")

            options_text = get_font(45).render("GAME OVER.", True, "white")
            options_rect = options_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(options_text, options_rect)

            restart_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (184, 56)),
                pos=(self.width // 2, self.height // 2 + self.height * 0.2),
                text_input="Restart", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            back_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (220, 56)),
                pos=(self.width // 2, self.height // 2 + self.height * 0.35),
                text_input="Main menu", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            restart_button.changeColor(options_mouse_pos)
            restart_button.update(self.screen)

            back_button.changeColor(options_mouse_pos)
            back_button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.play(self.cur_level)
                    if back_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.main_menu()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.main_menu()
                if event.type == SONG_ENDED:
                    self.sound.play_next_track()

            pygame.display.update()

    def win_screen(self):
        score = 0
        self.screen.fill("black")
        pygame.display.update()

        print(self.coin)

        coin_sprite = pygame.transform.scale(pygame.image.load("data/sprites/coin/5.png").convert_alpha(), (64, 64))
        pos_rot_coins = []
        for i in range(self.coin):
            pygame.time.delay(250)
            pos_rot_coins.append(
                (200 + 22 * i + randint(-10, 10), self.height // 2 - 100 + randint(-5, 5), randint(-90, 90)))
            self.screen.blit(pygame.transform.rotate(coin_sprite, pos_rot_coins[-1][2]),
                             (pos_rot_coins[-1][0], pos_rot_coins[-1][1]))
            pygame.display.update()
            self.sound.coin.play()

        life_sprite_0 = pygame.transform.scale(pygame.image.load("data/sprites/ui/0.png").convert_alpha(), (64, 56))
        life_sprite_1 = pygame.transform.scale(pygame.image.load("data/sprites/ui/1.png").convert_alpha(), (64, 56))
        for i in range(1, 4):
            pygame.time.delay(400)
            if i <= self.player.life:
                self.screen.blit(life_sprite_0, (130 + 70 * i, self.height // 2))
            else:
                self.screen.blit(life_sprite_1, (130 + 70 * i, self.height // 2))
            pygame.display.update()

        new_result = self.read_result()
        if int(new_result[self.cur_level][0]) < (100 * self.coin) * self.player.life:
            new_result[self.cur_level][0] = (100 * self.coin) * self.player.life
        self.write_result(new_result)

        while True:
            options_mouse_pos = pygame.mouse.get_pos()

            self.screen.fill("black")

            options_text = get_font(60).render("WIN.", True, "white")
            options_rect = options_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(options_text, options_rect)

            coin_text = get_font(80).render(f"x{self.coin}.", True, "white")
            coin_rect = coin_text.get_rect(topleft=(pos_rot_coins[-1][0] + 100, self.height // 2 - 100))
            self.screen.blit(coin_text, coin_rect)

            life_text = get_font(80).render(f"x{self.player.life}.", True, "white")
            life_rect = life_text.get_rect(topleft=(194 + 75 * 3, self.height // 2))
            self.screen.blit(life_text, life_rect)

            score_text = get_font(80).render(f"Score: {score}", True, "white")
            score_rect = score_text.get_rect(center=(self.width // 2 - 100, 200))
            self.screen.blit(score_text, score_rect)

            back_button = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (220, 56)),
                pos=(self.width // 2, self.height // 2 + self.height * 0.2),
                text_input="Main menu", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            back_button.changeColor(options_mouse_pos)
            back_button.update(self.screen)

            for x, y, r in pos_rot_coins:
                self.screen.blit(pygame.transform.rotate(coin_sprite, r), (x, y))

            for i in range(1, 4):
                if i <= self.player.life:
                    self.screen.blit(life_sprite_0, (130 + 70 * i, self.height // 2))
                else:
                    self.screen.blit(life_sprite_1, (130 + 70 * i, self.height // 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.main_menu()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.main_menu()
                if event.type == SONG_ENDED:
                    self.sound.play_next_track()

            if score < (100 * self.coin) * self.player.life:
                pygame.time.delay(80)
                score += 100

            pygame.display.update()

    def levels_screen(self):
        result = self.read_result()
        while True:
            options_mouse_pos = pygame.mouse.get_pos()

            self.screen.fill("black")

            options_text = get_font(80).render("Select level", True, "white")
            options_rect = options_text.get_rect(center=(self.width // 2, 40))
            self.screen.blit(options_text, options_rect)

            options_back = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (184, 56)),
                pos=(self.width // 2, self.height // 2 + self.height * 0.2),
                text_input="Back", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            options_back.changeColor(options_mouse_pos)
            options_back.update(self.screen)

            reset_result = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (200, 56)),
                pos=(self.width - 100, 28),
                text_input="Reset result", font=get_font(60), base_color="#d7fcd4", hovering_color="Red")

            reset_result.changeColor(options_mouse_pos)
            reset_result.update(self.screen)

            level_0 = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (184, 56)),
                pos=(self.width // 2 - 200, self.height // 2 - self.height * 0.1),
                text_input="level 1", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            level_1 = Button(
                image=pygame.transform.scale(pygame.image.load("data/sprites/ui/button.png").convert_alpha(),
                                             (184, 56)),
                pos=(self.width // 2 - 200, self.height // 2),
                text_input="level 2", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            score_text_0 = get_font(80).render(f"{result['level_0'][0]}/{result['level_0'][1]}", True, "white")
            score_rect_0 = options_text.get_rect(
                center=(self.width // 2 + 50, self.height // 2 - self.height * 0.1 - 10))
            self.screen.blit(score_text_0, score_rect_0)

            score_text_1 = get_font(80).render(f"{result['level_1'][0]}/{result['level_1'][1]}", True, "white")
            score_rect_1 = options_text.get_rect(center=(self.width // 2 + 50, self.height // 2 - 10))
            self.screen.blit(score_text_1, score_rect_1)

            level_0.changeColor(options_mouse_pos)
            level_0.update(self.screen)

            level_1.changeColor(options_mouse_pos)
            level_1.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if level_0.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.cur_level = "level_0"
                        self.play(self.cur_level)
                    if level_1.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.cur_level = "level_1"
                        self.play(self.cur_level)
                    if options_back.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.main_menu()
                    if reset_result.checkForInput(options_mouse_pos):
                        self.sound.ui_click.play()
                        self.reset_save()
                        result = self.read_result()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.main_menu()
                if event.type == SONG_ENDED:
                    self.sound.play_next_track()

            pygame.display.update()

    def read_result(self):
        with open(self.path_to_save) as save:
            result = save.read().splitlines()
            re = {line.split()[0]: [line.split()[1], line.split()[2]] for line in result}
        return re

    def write_result(self, new_save):
        with open(self.path_to_save, "w") as save:
            for level, value in new_save.items():
                save.write(f"{level} {value[0]} {value[1]}\n")

    def reset_save(self):
        self.write_result({level: [0, value[1]] for level, value in self.read_result().items()})
