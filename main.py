from core import *
from config import *

class KoiKoiGame(Game):
    def start(self):
        import scene
        self.scene = scene

    def update(self):
        self.scene.game_context.update()

Runner.run(
    window_title = WINDOW_TITLE, 
    flags = pygame.FULLSCREEN,
    game = KoiKoiGame()
)