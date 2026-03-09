from core import *
from config import *
from interface import *

class KoiKoiGameObject(GameObject):
    def __init__(
            self, 
            context : Context, 
            x : float = 0, 
            y : float = 0, 
            width : float = 0, 
            height : float = 0, 
            sprite : Sprite = None, 
            color : tuple[int, int, int] = (0, 0, 0), 
            tag = None
        ):

        super().__init__(
            context = context, 
            x = x, 
            y = y, 
            width = width, 
            height = height, 
            sprite = sprite, 
            color = color, 
            tag = tag
        )

    def render(self):
        if DEBUG_SHOW_RECTS:
            pygame.draw.rect(Window.screen, self.color, self.rect)
        
        super().render()

class Card(KoiKoiGameObject):
    def __init__(
            self, 
            context : Context, 
            x : float,
            y : float,
            card_type : int,
            faceup : bool
        ):

        width = 0
        height = 0
        sprite = None
        card_month = 0

        if card_type == CARD_TYPE_PINE_CRANE:
            width = CARD_PINE_CRANE_RECT_WIDTH
            height = CARD_PINE_CRANE_RECT_HEIGHT
            sprite = CARD_PINE_CRANE_SPRITE
            card_month = JANUARY
        elif card_type == CARD_TYPE_PINE_PLAIN1:
            width = CARD_PINE_PLAIN1_RECT_WIDTH
            height = CARD_PINE_PLAIN1_RECT_HEIGHT
            sprite = CARD_PINE_PLAIN1_SPRITE
            card_month = JANUARY
        elif card_type == CARD_TYPE_PINE_PLAIN2:
            width = CARD_PINE_PLAIN2_RECT_WIDTH
            height = CARD_PINE_PLAIN2_RECT_HEIGHT
            sprite = CARD_PINE_PLAIN2_SPRITE
            card_month = JANUARY
        elif card_type == CARD_TYPE_PINE_RED_POEM_TANZAKU:
            width = CARD_PINE_RED_POEM_TANZAKU_RECT_WIDTH
            height = CARD_PINE_RED_POEM_TANZAKU_RECT_HEIGHT
            sprite = CARD_PINE_RED_POEM_TANZAKU_SPRITE
            card_month = JANUARY

        self.card_front_sprite = sprite
        self.card_month = card_month

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            sprite = sprite,
            color = CARD_RECT_COLOR
        )

        self.faceup = faceup

    @property
    def faceup(self) -> bool:
        return self._faceup
    
    @faceup.setter
    def faceup(self, value : bool):
        self._faceup = value

        if value:
            self.sprite = self.card_front_sprite
        else:
            self.sprite = CARD_BACK_SPRITE

    def move_to(self, destination : Vector2):
        self.start_timed_task(self.move_to_task(destination))
    
    def move_to_task(self, destination : Vector2) -> Task:
        max_speed = 200
        min_speed = 12

        initial_distance_sq = Vector2.distance_between_sq(self.position, destination)

        while True:
            distance_sq = Vector2.distance_between_sq(self.position, destination)

            if distance_sq == 0:
                break

            ratio = distance_sq / initial_distance_sq
            velocity = max(min_speed, max_speed * ratio)

            Vector2.move_towards(self.position, destination, velocity)

            yield 0

class CardSlot(KoiKoiGameObject):
    def __init__(
            self,
            context : Context,
            x : float,
            y : float
        ):

        self.card : Card = None

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = CARD_SLOT_RECT_WIDTH,
            height = CARD_SLOT_RECT_HEIGHT,
            color = CARD_SLOT_RECT_COLOR
        )

    def is_free(self) -> bool:
        return self.card == None

    def bind(self, card : Card):
        self.card = card

class CardSlotManager(interface):
    def make_slots(self) -> list[CardSlot]:
        pass

    def set(self, card : Card):
        pass

    def get_free_slot(self) -> CardSlot:
        pass

@implements(CardSlotManager)
class CardTable(KoiKoiGameObject):
    def __init__(
            self,
            context : Context,
            x : float,
            y : float    
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = CARD_TABLE_RECT_WIDTH,
            height = CARD_TABLE_RECT_HEIGHT,
            color = CARD_TABLE_RECT_COLOR
        )

        self.slots : list[CardSlot] = self.make_slots()
    
    def make_slots(self) -> list[CardSlot]:
        slots : list[CardSlot] = []

        for y in range(0, 2):
            cy = self.rect.y + CARD_RECT_HEIGHT * y + CARD_SLOT_Y_OFFSET * y

            for x in range(0, 5):
                cx = self.rect.x + CARD_RECT_WIDTH * x + CARD_SLOT_X_OFFSET * x

                slot = CardSlot(self.context, cx, cy)
                slots.append(slot)
        
        return slots
    
    def set(self, card : Card):
        slot = self.get_free_slot()

        if slot != None:
            slot.bind(card)

    def get_free_slot(self) -> CardSlot:
        for slot in self.slots:
            if slot.is_free():
                return slot
        
        return None

@implements(CardSlotManager)
class CardHand(KoiKoiGameObject):
    def __init__(
            self,
            context : Context,
            x : float,
            y : float    
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = CARD_HAND_RECT_WIDTH,
            height = CARD_HAND_RECT_HEIGHT,
            color = CARD_HAND_RECT_COLOR
        )

        self.slots = self.make_slots()

    def make_slots(self) -> list[CardSlot]:
        slots : list[CardSlot] = []

        for x in range(0, 8):
            cx = self.rect.x + x * CARD_RECT_WIDTH + x * CARD_SLOT_X_OFFSET

            slot = CardSlot(self.context, cx, self.rect.y)
            slots.append(slot)
        
        return slots
    
    def set(self, card : Card):
        slot = self.get_free_slot()

        if slot != None:
            slot.bind(card)

    def get_free_slot(self) -> CardSlot:
        for slot in self.slots:
            if slot.is_free():
                return slot
        
        return None

class CardDeck(KoiKoiGameObject):
    def __init__(
            self,
            context : Context,
            x : float,
            y : float,
            card_table : CardTable,
            player_hand : CardHand,
            opponent_hand : CardHand
        ):

        super().__init__(
            context = context,
            x = x,
            y = y
        )

        self.cards : list[Card] = self.make_cards()
        self.card_table = card_table
        self.player_hand = player_hand
        self.opponent_hand = opponent_hand

    def start(self):
        self.start_timed_task(self.distribute_cards())

    def make_cards(self) -> list[Card]:
        cards : list[Card] = []

        for i in range(0, 40):
            card = Card(self.context, self.rect.x - i, self.rect.y, CARD_TYPE_PINE_PLAIN2, False)
            cards.append(card)

        return cards

    def distribute_cards(self) -> Task:
        table_slot = self.card_table.get_free_slot()
        player_hand_slot = self.player_hand.get_free_slot()
        opponent_hand_slot = self.opponent_hand.get_free_slot()

        while len(self.cards) > 0 and (table_slot != None or player_hand_slot != None or opponent_hand_slot != None):
            if opponent_hand_slot != None:
                self.deck_top_to_slot(opponent_hand_slot)
                yield 333
            if player_hand_slot != None:
                self.deck_top_to_slot(player_hand_slot)
                yield 333
            if table_slot != None:
                self.deck_top_to_slot(table_slot, True)
                yield 333
            
            table_slot = self.card_table.get_free_slot()
            player_hand_slot = self.player_hand.get_free_slot()
            opponent_hand_slot = self.opponent_hand.get_free_slot()

        yield 0
    
    def deck_top_to_slot(self, slot : CardSlot, faceup : bool = False):
            if len(self.cards) == 0:
                return

            top_card = self.cards.pop()

            if faceup:
                top_card.faceup = True

            top_card.move_to(slot.position)
            slot.bind(top_card)