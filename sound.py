from pygame import mixer
from random import randint


class SoundModule:
    def __init__(self, event_song_end):
        self.list_music = ["data/music/afternoonisms.mp3", "data/music/Bluesy.mp3", "data/music/Idiophonix.mp3",
                           "data/music/UnderwaterLevel.mp3"]
        self.cur_track = randint(0, len(self.list_music) - 1)

        self.path_to_settings = "data/save/settings.txt"

        self.volume_ui, self.volume_music = self.read_settings()
        self.read_settings()

        self.coin = mixer.Sound("data/sounds/coin.wav")

        self.ui_click = mixer.Sound("data/sounds/cursor_sound.wav")
        self.set_volume_ui(self.volume_ui)
        mixer.music.set_endevent(event_song_end)
        self.set_volume_music(self.volume_music)
        self.play_next_track()

    def play_next_track(self):
        mixer.music.load(self.list_music[self.cur_track])
        mixer.music.play()
        mixer.music.get_pos()
        self.cur_track = (self.cur_track + 1) % len(self.list_music)

    def read_settings(self):
        with open(self.path_to_settings) as save:
            volumes = save.readlines()
        return float(volumes[0]), float(volumes[1])

    def write_settings(self, new_settings):
        with open(self.path_to_settings, "w") as save:
            save.write("\n".join([str(i) for i in new_settings]))

    def set_volume_ui(self, volume):
        self.ui_click.set_volume(volume)

    def set_volume_music(self, volume):
        mixer.music.set_volume(volume)
