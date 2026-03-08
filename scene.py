from core import *
from game import *
from utils import *

game_context = Context()

card_ground = CardTable(game_context, center_x(CARD_TABLE_RECT_WIDTH), center_y(CARD_TABLE_RECT_HEIGHT))
player_hand = CardHand(game_context, center_x(CARD_HAND_RECT_WIDTH), Window.height - CARD_HAND_RECT_HEIGHT)
opponent_hand = CardHand(game_context, center_x(CARD_HAND_RECT_WIDTH), 0)
card_deck = CardDeck(game_context, 50, center_y(CARD_RECT_HEIGHT), card_ground, player_hand, opponent_hand)