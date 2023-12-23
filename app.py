from main import Game

app = Game((360, 240))
app.load_level("data/levels/level_0.tmx")

while True:
    app.update()
