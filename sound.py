from pygame import mixer
from random import randint


class SoundModule:
    def __init__(self, event_song_end, current_volume):
        self.list_music = ["data/music/afternoonisms.mp3", "data/music/Bluesy.mp3", "data/music/Idiophonix.mp3",
                           "data/music/UnderwaterLevel.mp3"]
        self.cur_track = randint(0, len(self.list_music) - 1)

        self.path_to_settings = "data/save/settings.txt"
        self.volume_ui, self.volume_music = current_volume

        self.coin = mixer.Sound("data/sounds/coin.wav")

        self.ui_click = mixer.Sound("data/sounds/cursor_sound.wav")
        self.set_volume_ui(self.volume_ui)
        mixer.music.set_endevent(event_song_end)
        self.set_volume_music(self.volume_music)
        self.play_next_track()

    def play_next_track(self):
        mixer.music.load(self.list_music[self.cur_track])
        mixer.music.play()
        self.cur_track = (self.cur_track + 1) % len(self.list_music)

    def set_volume_ui(self, volume):
        self.ui_click.set_volume(volume)
        
    def set_volume_music(self, volume):
        mixer.music.set_volume(volume)
