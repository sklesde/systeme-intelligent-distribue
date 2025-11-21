__author__ = "Student helper"
__license__ = "Apache License 2.0"

import os
import json
import pygame


def load_map_size(map_id=1):
    """Return (width, height) for the given map id."""
    json_filename = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "resources",
        "config.json",
    )
    with open(json_filename, "r") as json_file:
        cfg = json.load(json_file)[f"map_{map_id}"]
    return cfg["width"], cfg["height"]


# Predefined example paths for two robots (left and right)
list_1 = [
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
list_2 = [
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








class PathListEditor:
    """
    Simple interactive grid editor.

    - Left click: color a cell with the currently selected color.
    - Right click: erase (back to white).
    - Keys 1..6: select a color.
        1 -> blue
        2 -> red
        3 -> orange
        4 -> green
        5 -> black
        6 -> violet
        0 -> erase (white)
    - Click "Valider" button: print, in the console, for each color,
      the list of (x, y) tuples that have this color.
    """

    def __init__(self, map_id=1, cell_size=20):
        self.map_w, self.map_h = load_map_size(map_id)
        self.cell_size = cell_size

        # Pygame setup
        pygame.init()
        # We add a small panel at the bottom for the validate button.
        self.panel_height = 60
        self.screen = pygame.display.set_mode(
            (self.map_w * self.cell_size, self.map_h * self.cell_size + self.panel_height)
        )
        pygame.display.set_caption("Path List Editor")
        self.clock = pygame.time.Clock()
        self.running = True

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.ORANGE = (255, 165, 0)
        self.GREEN = (0, 255, 0)
        self.VIOLET = (148, 0, 211)
        self.BG_PANEL = (230, 230, 230)

        # Mapping color indices -> (name, rgb)
        # 0 is "no color" (white background).
        self.color_map = {
            0: ("none", self.WHITE),
            1: ("blue", self.BLUE),
            2: ("red", self.RED),
            3: ("orange", self.ORANGE),
            4: ("green", self.GREEN),
            5: ("black", self.BLACK),
            6: ("violet", self.VIOLET),
        }

        # Grid state: for each (x, y), store an integer color index.
        self.grid = [
            [0 for _ in range(self.map_w)] for _ in range(self.map_h)
        ]

        # Current selected color index (default: 1 -> blue)
        self.current_color_idx = 1

        # Mouse state for click-and-drag painting
        self.mouse_button_held = None  # 1 = left (paint), 3 = right (erase)
        self.dragging_in_grid = False

        # Validate button rectangle (placed on the right side of the bottom panel)
        btn_width = 120
        btn_height = 40
        btn_x = self.map_w * self.cell_size - btn_width - 20
        btn_y = self.map_h * self.cell_size + (self.panel_height - btn_height) // 2
        self.validate_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        self.font = pygame.font.SysFont("Arial", 18, True)

        # Palette of colors (including eraser) shown at the bottom.
        # We precompute a rect for each color index.
        self.palette_rects = {}
        palette_indices = [0, 1, 2, 3, 4, 5, 6]
        box_size = 30
        spacing = 10
        start_x = 20
        center_y = self.map_h * self.cell_size + self.panel_height // 2
        top_y = center_y - box_size // 2
        for i, idx in enumerate(palette_indices):
            x = start_x + i * (box_size + spacing)
            self.palette_rects[idx] = pygame.Rect(x, top_y, box_size, box_size)

    def apply_list(self, points, color_idx):
        """
        Color all cells whose coordinates are given in 'points'
        with the color index 'color_idx'.

        'points' should be an iterable of (x, y) tuples.
        """
        if color_idx not in self.color_map:
            return
        for x, y in points:
            if 0 <= x < self.map_w and 0 <= y < self.map_h:
                self.grid[y][x] = color_idx

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            self.clock.tick(30)
        pygame.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Click on validate button?
            if self.validate_rect.collidepoint(x, y):
                self.on_validate()
                return

            # Click in palette?
            for idx, rect in self.palette_rects.items():
                if rect.collidepoint(x, y):
                    self.current_color_idx = idx
                    return

            # Click inside the grid?
            if y < self.map_h * self.cell_size:
                grid_x = x // self.cell_size
                grid_y = y // self.cell_size
                if 0 <= grid_x < self.map_w and 0 <= grid_y < self.map_h:
                    if event.button == 1:  # left click -> paint
                        self.grid[grid_y][grid_x] = self.current_color_idx
                        self.mouse_button_held = 1
                        self.dragging_in_grid = True
                    elif event.button == 3:  # right click -> erase
                        self.grid[grid_y][grid_x] = 0
                        self.mouse_button_held = 3
                        self.dragging_in_grid = True
            else:
                self.mouse_button_held = None
                self.dragging_in_grid = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                self.mouse_button_held = None
                self.dragging_in_grid = False

        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_button_held in (1, 3) and self.dragging_in_grid:
                x, y = event.pos
                if y < self.map_h * self.cell_size:
                    grid_x = x // self.cell_size
                    grid_y = y // self.cell_size
                    if 0 <= grid_x < self.map_w and 0 <= grid_y < self.map_h:
                        if self.mouse_button_held == 1:
                            self.grid[grid_y][grid_x] = self.current_color_idx
                        elif self.mouse_button_held == 3:
                            self.grid[grid_y][grid_x] = 0

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                self.current_color_idx = 0
            elif event.key == pygame.K_1:
                self.current_color_idx = 1
            elif event.key == pygame.K_2:
                self.current_color_idx = 2
            elif event.key == pygame.K_3:
                self.current_color_idx = 3
            elif event.key == pygame.K_4:
                self.current_color_idx = 4
            elif event.key == pygame.K_5:
                self.current_color_idx = 5
            elif event.key == pygame.K_6:
                self.current_color_idx = 6

    def draw(self):
        # Draw grid background
        self.screen.fill(self.WHITE)

        # Draw colored cells
        for y in range(self.map_h):
            for x in range(self.map_w):
                color_idx = self.grid[y][x]
                name, color = self.color_map[color_idx]
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                )

        # Draw grid lines
        for i in range(1, self.map_h):
            pygame.draw.line(
                self.screen,
                self.BLACK,
                (0, i * self.cell_size),
                (self.map_w * self.cell_size, i * self.cell_size),
            )
        for j in range(1, self.map_w):
            pygame.draw.line(
                self.screen,
                self.BLACK,
                (j * self.cell_size, 0),
                (j * self.cell_size, self.map_h * self.cell_size),
            )

        # Draw bottom panel
        pygame.draw.rect(
            self.screen,
            self.BG_PANEL,
            pygame.Rect(
                0, self.map_h * self.cell_size, self.map_w * self.cell_size, self.panel_height
            ),
        )

        # Draw color palette
        for idx, rect in self.palette_rects.items():
            name, color = self.color_map[idx]
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, width=2)
            # Optional small label for the index
            label = "E" if idx == 0 else str(idx)
            text = self.font.render(label, True, self.BLACK if idx != 5 else self.WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Validate button
        pygame.draw.rect(self.screen, self.BLACK, self.validate_rect, width=2)
        text = self.font.render("Valider", True, self.BLACK)
        text_rect = text.get_rect(center=self.validate_rect.center)
        self.screen.blit(text, text_rect)

        # Current color indicator (simple text)
        name, color = self.color_map[self.current_color_idx]
        info_text = self.font.render(f"Couleur: {name}", True, self.BLACK)
        self.screen.blit(info_text, (10, self.map_h * self.cell_size + 5))

        pygame.display.flip()

    def on_validate(self):
        """
        Print, for each color, the list of (x, y) coordinates
        that have this color.
        """
        color_points = {idx: [] for idx in self.color_map.keys() if idx != 0}

        for y in range(self.map_h):
            for x in range(self.map_w):
                idx = self.grid[y][x]
                if idx != 0:
                    color_points[idx].append((x, y))

        print("=== Path lists by color ===")
        for idx, points in color_points.items():
            name, _ = self.color_map[idx]
            print(f"{name}: {points}")


if __name__ == "__main__":
    editor = PathListEditor(map_id=1)
    # If you define lists named list_1, list_2, ... at the top of this file,
    # they will be drawn automatically with different colors.
    globals_dict = globals()
    predefined = [
        ("list_1", 1),
        ("list_2", 2),
        ("list_3", 3),
        ("list_4", 4),
        ("list_5", 5),
        ("list_6", 6),
    ]
    for name, color_idx in predefined:
        if name in globals_dict:
            editor.apply_list(globals_dict[name], color_idx)

    editor.run()
