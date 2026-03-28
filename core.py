import pygame
import math
from typing import Callable, final, Generator

Task = Generator[int, None, None]
Color = tuple[int, int, int]

class Game:
    def start(self):
        pass

    def update(self):
        pass

@final
class Runner:
    @staticmethod
    def run(window_width : int = 0, window_height : int = 0, window_title : str = 0, flags : int = 0, game : Game = None):
        pygame.init()
        Window.init(window_width, window_height, window_title, flags)

        clock = pygame.time.Clock()
        game.start()

        running = True

        while running:
            Input.keys_down.clear()
            Input.keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    Input.keys_down.append(event.key)

            Window.screen.fill((0, 0, 0))

            game.update()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

@final
class Window:
    screen : pygame.Surface = None
    width : int = 0
    height : int = 0

    @staticmethod
    def init(window_width : int = 0, window_height : int = 0, window_title : str = "Game", flags : int = 0):
        Window.screen = pygame.display.set_mode((window_width, window_height), flags)
        Window.width, Window.height = Window.screen.get_size()
        pygame.display.set_caption(window_title)

@final
class Sprite:
    def __init__(
            self,
            surface : pygame.Surface
        ):
            self.surface = surface

    def blend(self, color : Color) -> 'Sprite':
        surface = self.surface.copy().convert_alpha()
        surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

        return Sprite(surface)

    @staticmethod
    def load(resource : str, width : int, height : int):
        surface = pygame.image.load(resource)
        surface = pygame.transform.scale(surface, (width, height))

        return Sprite(surface)

@final
class Context:
    """
    Represents a container that manages and updates all GameObjects instances it contains.

    GameObjects are grouped by their `tag` and are stored in buckets inside a dictionary.
    Each tag maps to a key of the dictionary.

    Methods
    ----------
    update()
        Iterates through all GameObjects and calls their `_update` function.
        Removes objects marked as `destroyed`.
    
    append()
        Adds a `GameObject` to the context. The object is inserted in the bucket associated with its tag.
        This method should **NOT** be called by the user as it is arleady called by the GameObject's constructor.

    find_with_tag()
        Returns a list of GameObjects associated with the given `tag`.
    """
    def __init__(self):
        self.game_objects : dict[str, list[GameObject]] = {}

    def update(self):
        tags = list(self.game_objects.keys())

        for tag in tags:
            bucket = self.game_objects[tag]

            lenght = len(bucket)
            index = 0

            while index < lenght:
                if bucket[index].destroyed:
                    bucket.pop(index)
                    continue
                else:
                    bucket[index]._update()

                index += 1

    def append(self, game_object : 'GameObject'):
        bucket = self.game_objects.get(game_object.tag, None)

        if bucket == None:
            self.game_objects[game_object.tag] = [game_object]
        else:
            bucket.append(game_object)

    def find_with_tag(self, tag : str) -> list['GameObject']:
        return self.game_objects[tag]
    
    def bring_to_front(self, game_object : 'GameObject'):
        bucket = self.find_with_tag(game_object.tag)
        bucket.remove(game_object)
        bucket.append(game_object)

class Vector2:
    def __init__(self, x : float, y : float):
        self.x = float(x)
        self.y = float(y)
    
    def lenght_sq(self):
        return self.x * self.x + self.y * self.y
    
    def lenght(self):
        return math.sqrt(self.lenght_sq())
    
    def normalize(self):
        lenght = self.lenght()

        if lenght == 0:
            return Vector2(0, 0)
        
        return Vector2(self.x / lenght, self.y / lenght)
    
    @staticmethod
    def distance_between_sq(a : 'Vector2', b : 'Vector2') -> float:
        return (b.x - a.x) ** 2 + (b.y - a.y) ** 2
    
    @staticmethod
    def distance_between(a : 'Vector2', b : 'Vector2') -> float:
        return math.sqrt(Vector2.distance_between_sq(a, b))

    @staticmethod
    def move_towards(a : 'Vector2', b : 'Vector2', speed : float):
        direction = Vector2(b.x - a.x, b.y - a.y)

        dist_sq = direction.lenght_sq()

        if dist_sq == 0:
            return
        
        if dist_sq <= speed * speed:
            a.x = b.x
            a.y = b.y
            return
        
        direction = direction.normalize()

        a.x += direction.x * speed
        a.y += direction.y * speed

@final
class TimedTask:
    """
    Represents a time controlled task driven by a generator.

    The generator yields `int` values representing a delay in milliseconds, that determine when the next iteration should be.
    Each time `update` is called, the tasks checks if enough time has passed to resume the generator.
    """
    def __init__(self, generator : Callable):
        self.generator = generator

        self.is_finished = False
        self.next_iteration = 0
    
    def update(self):
        if self.is_finished:
            return

        current_time = pygame.time.get_ticks()

        if current_time >= self.next_iteration:
            try:
                delay = next(self.generator)

                self.next_iteration = current_time + delay
                
            except StopIteration:
                self.is_finished = True

class GameObject:
    def __init__(
            self,
            context : Context,
            x : float = 0,
            y : float = 0,
            width : float = 0,
            height : float = 0,
            sprite: Sprite = None,
            color : Color = (0, 0, 0),
            tag : str = None
        ):

        self.context = context
        self.tag = tag
        self.rect = pygame.Rect(float(x), float(y), float(width), float(height))
        self.color = color
        self.sprite = sprite

        self.hidden = False
        self.destroyed = False
        self.timed_tasks : list[TimedTask] = []
        self._position = Vector2(self.rect.x, self.rect.y)

        context.append(self)

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, position : Vector2):
        self._position = position

    @final
    def _update(self):
        self.start()
        self._sync_pos()
        
        self._update = self._update_after_start
    @final
    def _update_after_start(self):
        self.update()
        self._sync_pos()

        taskidx = 0

        while taskidx < len(self.timed_tasks):
            if self.timed_tasks[taskidx].is_finished:
                self.timed_tasks.pop(taskidx)
            else:
                self.timed_tasks[taskidx].update()
                taskidx += 1

        self.render()

    @final
    def _sync_pos(self):
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def start(self):
        pass

    def update(self):
        pass

    def render(self):
        if self.sprite != None:
            Window.screen.blit(self.sprite.surface, self.rect)

    @final
    def destroy(self):
        self.destroyed = True

    @final
    def collide(self, other : 'GameObject') -> bool:
        if self.destroyed or other.destroyed:
            return False

        return self.rect.colliderect(other.rect)
    
    @final
    def start_timed_task(self, func : Callable):
        self.timed_tasks.append(TimedTask(func))

    def bring_to_front(self):
        self.context.bring_to_front(self)

@final
class Input:
    keys = None
    keys_down : list[int] = []

    @staticmethod
    def get_key(key : int) -> bool:
        return Input.keys[key]

    @staticmethod
    def get_key_down(key : int) -> bool:
        return key in Input.keys_down