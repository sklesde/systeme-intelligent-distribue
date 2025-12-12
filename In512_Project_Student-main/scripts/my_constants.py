__author__ = "Aybuke Ozturk Suri, Johvany Gustave"
__copyright__ = "Copyright 2023, IN512, IPSA 2024"
__credits__ = ["Aybuke Ozturk Suri", "Johvany Gustave"]
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

""" This file contains all the 'constants' shared by all the scripts """

""" MSG HEADERS """
BROADCAST_MSG = 0
GET_DATA = 1    #get the current location of the agent and the dimension of the environment (width and height)
MOVE = 2
GET_NB_CONNECTED_AGENTS = 3
GET_NB_AGENTS = 4
GET_ITEM_OWNER = 5

""" ALLOWED MOVES """
STAND = 0   #do not move
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4
UP_LEFT = 5
UP_RIGHT = 6
DOWN_LEFT = 7
DOWN_RIGHT = 8

""" BROADCAST TYPES """
KEY_DISCOVERED = 1  #inform other agents that you discovered a key
BOX_DISCOVERED = 2
COMPLETED = 3   #inform other agents that you discovered your key and you reached your own box

""" GAME """
GAME_ID = -1    #id of the game when it sends a message to an agent
KEY_NEIGHBOUR_PERCENTAGE = 0.5  #value of an adjacent cell to a key
BOX_NEIGHBOUR_PERCENTAGE = 0.6  #value of an adjacent cell to a key
WALLS_NEIGHBOUR_PERCENTAGE = 0.35
KEY_TYPE = 0    #one of the types of item that is output by the 'Get item owner' request
BOX_TYPE = 1

""" GUI """
BG_COLOR = (255, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

list_0 = [
    (2, 6), (2, 5), (2, 4), (2, 3), (2, 2),
    (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
    (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
    (13, 2), (14, 2), (15, 2), (16, 2), (17, 2),
    (18, 2), (19, 2), (20, 2), (21, 2), (22, 2),
    (23, 2), (24, 2), (25, 2), (26, 2), (27, 2),
    (28, 2), (29, 2), (30, 2), (31, 2), (32, 2),

    (32, 3), (32, 4), (32, 5), (32, 6),

    (31, 7), (30, 7), (29, 7), (28, 7), (27, 7),
    (26, 7), (25, 7), (24, 7), (23, 7), (22, 7),
    (21, 7), (20, 7), (19, 7), (18, 7), (17, 7),
    (16, 7), (15, 7), (14, 7), (13, 7), (12, 7),
    (11, 7), (10, 7), (9, 7), (8, 7), (7, 7),
    (6, 7), (5, 7), (4, 7), (3, 7),

    (2, 7),
    (2, 8), (2, 9), (2, 10), (2, 11), (2, 12),

    (3, 12), (4, 12), (5, 12), (6, 12), (7, 12),
    (8, 12), (9, 12), (10, 12), (11, 12), (12, 12),
    (13, 12), (14, 12), (15, 12), (16, 12), (17, 12),
    (18, 12), (19, 12), (20, 12), (21, 12), (22, 12),
    (23, 12), (24, 12), (25, 12), (26, 12), (27, 12),
    (28, 12), (29, 12), (30, 12), (31, 12), (32, 12),

    (32, 11), (32, 10), (32, 9), (32, 8)
]

list_1 = [
    (2, 21), (2, 20), (2, 19), (2, 18), (2, 17),
    (3, 17), (4, 17), (5, 17), (6, 17), (7, 17),
    (8, 17), (9, 17), (10, 17), (11, 17), (12, 17),
    (13, 17), (14, 17), (15, 17), (16, 17), (17, 17),
    (18, 17), (19, 17), (20, 17), (21, 17), (22, 17),
    (23, 17), (24, 17), (25, 17), (26, 17), (27, 17),
    (28, 17), (29, 17), (30, 17), (31, 17), (32, 17),

    (32, 18), (32, 19), (32, 20), (32, 21),

    (31, 22), (30, 22), (29, 22), (28, 22), (27, 22),
    (26, 22), (25, 22), (24, 22), (23, 22), (22, 22),
    (21, 22), (20, 22), (19, 22), (18, 22), (17, 22),
    (16, 22), (15, 22), (14, 22), (13, 22), (12, 22),
    (11, 22), (10, 22), (9, 22), (8, 22), (7, 22),
    (6, 22), (5, 22), (4, 22), (3, 22),

    (2, 22),
    (2, 23), (2, 24), (2, 25), (2, 26), (2, 27),

    (3, 27), (4, 27), (5, 27), (6, 27), (7, 27),
    (8, 27), (9, 27), (10, 27), (11, 27), (12, 27),
    (13, 27), (14, 27), (15, 27), (16, 27), (17, 27),
    (18, 27), (19, 27), (20, 27), (21, 27), (22, 27),
    (23, 27), (24, 27), (25, 27), (26, 27), (27, 27),
    (28, 27), (29, 27), (30, 27), (31, 27), (32, 27),

    (32, 26), (32, 25), (32, 24), (32, 23)
]

lists = {
    0: list_0,
    1: list_1,
}
