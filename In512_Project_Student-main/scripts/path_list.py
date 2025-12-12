__author__ = "Student helper"
__license__ = "Apache License 2.0"

import os
import json
import pygame
from typing import List, Dict, Tuple


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


# --- exemples prédéfinis (gardés pour compatibilité) ---
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


# ----------------- Fonctions de génération des paths -----------------
def _split_into_parts(total: int, k: int) -> List[int]:
    """Divise 'total' en k parts entières aussi égales que possible."""
    if k <= 0:
        return []
    k = min(k, total)
    base = total // k
    rem = total % k
    parts = [base + (1 if i < rem else 0) for i in range(k)]
    return parts


def _perimeter_points(x0: int, x1: int, y0: int, y1: int) -> List[Tuple[int, int]]:
    """
    Retourne la liste ordonnée des coordonnées du périmètre du rectangle
    bordé par [x0..x1] x [y0..y1] (parcours horaire).
    """
    pts: List[Tuple[int, int]] = []
    if x0 > x1 or y0 > y1:
        return pts
    # cas lignes/colonnes dégénérées
    if y0 == y1:
        for x in range(x0, x1 + 1):
            pts.append((x, y0))
        return pts
    if x0 == x1:
        for y in range(y0, y1 + 1):
            pts.append((x0, y))
        return pts

    # gauche du haut vers le bas
    for y in range(y0, y1 + 1):
        pts.append((x0, y))
    # bas de gauche+1 vers droite
    for x in range(x0 + 1, x1 + 1):
        pts.append((x, y1))
    # droite du bas-1 vers haut
    for y in range(y1 - 1, y0 - 1, -1):
        pts.append((x1, y))
    # haut de droite-1 vers gauche+1 (évite répéter le premier point)
    for x in range(x1 - 1, x0, -1):
        pts.append((x, y0))
    return pts
def _allocate_widths_and_gaps(total: int, k: int, min_gap: int = 1, max_gap: int = 4):
    """
    Calcule deux listes : widths (len=k) et gaps (len=k-1) telles que :
     - sum(widths) + sum(gaps) == total
     - chaque width >= 1
     - chaque gap in [min_gap, max_gap]
    Stratégie :
     - Réserver min_gap pour chaque gap.
     - Distribuer une largeur de base aux k segments.
     - Répartir l'espace restant d'abord sur les gaps (jusqu'à max_gap),
       puis sur les widths (round-robin).
    Lève ValueError si impossible.
    """
    if k <= 0:
        return [], []
    if k == 1:
        return [total], []

    # espace minimal demandé par les gaps
    min_total_gaps = (k - 1) * min_gap
    # chaque segment a au moins largeur 1
    min_total_segments = k * 1
    if total < (min_total_segments + min_total_gaps):
        raise ValueError("Taille totale trop petite pour placer les segments avec les gaps demandés.")

    # initialisation
    gaps = [min_gap] * (k - 1)
    # allouer une largeur de base aux segments
    remaining_after_gaps = total - sum(gaps)
    base_width = remaining_after_gaps // k
    if base_width < 1:
        base_width = 1
    widths = [base_width] * k

    remaining = total - (sum(widths) + sum(gaps))

    # 1) essayer d'augmenter d'abord les gaps jusqu'à max_gap (préférence pour espacer)
    gi = 0
    # on parcourt les gaps en cycle tant qu'il reste à distribuer
    while remaining > 0 and any(g < max_gap for g in gaps):
        can = max_gap - gaps[gi]
        if can > 0:
            add = min(can, remaining)
            gaps[gi] += add
            remaining -= add
        gi = (gi + 1) % len(gaps)

    # 2) si reste encore, on distribue aux widths en round-robin
    wi = 0
    while remaining > 0:
        widths[wi] += 1
        remaining -= 1
        wi = (wi + 1) % k

    # vérification rapide
    if sum(widths) + sum(gaps) != total:
        # Ajustement final si problème d'arrondis (corrige en ajoutant/reduisant le dernier width)
        diff = total - (sum(widths) + sum(gaps))
        widths[-1] += diff

    return widths, gaps


def generate_rect_paths(n: int, m: int, k: int, margin: int = 2,
                        min_gap: int = 1, max_gap: int = 4,
                        allow_multiple_per_color: bool = True):
    """
    Génère des paths (périmètres rectangulaires intérieurs) pour une map n x m.
    - k : nombre de robots (2..4)
    - margin : marge au bord (par défaut 2)
    - min_gap / max_gap : espacement entre rectangles successifs (en cases)
    - allow_multiple_per_color : si True, on peut attribuer plusieurs rectangles à une même couleur.
    Retour : dictionnaire {color_idx: [(x,y), ...], ...} où color_idx ∈ [0..k-1].
    """
    if k < 2 or k > 4:
        raise ValueError("k doit être entre 2 et 4 (inclus).")
    if n <= 2 * margin or m <= 2 * margin:
        raise ValueError("La map est trop petite pour la marge demandée.")

    x0 = margin
    x1 = m - 1 - margin
    y0 = margin
    y1 = n - 1 - margin

    width = x1 - x0 + 1
    height = y1 - y0 + 1
    horizontal_long = (width >= height)

    # helper: nombre max de rectangles possible si chaque rectangle >=1 et gap >= min_gap
    def max_possible_rects(total_len, min_gap):
        # pour R rectangles il faut : total_len >= R + (R-1)*min_gap
        # => R <= floor((total_len + min_gap) / (1 + min_gap))
        return (total_len + min_gap) // (1 + min_gap)

    total = width if horizontal_long else height
    max_rects = max_possible_rects(total, min_gap)

    if allow_multiple_per_color:
        # viser jusqu'à 2 rectangles par robot si possible
        target_R = min(max_rects, 2 * k)
        # si on ne peut même pas avoir k rectangles, on essaie d'avoir au moins max_rects
        if target_R < k:
            target_R = min(max_rects, k)
    else:
        target_R = min(max_rects, k)

    if target_R <= 0:
        raise ValueError("Dimension interne trop petite pour placer des rectangles avec les gaps demandés.")

    # allocation des largeurs et gaps le long de la dimension
    widths, gaps = _allocate_widths_and_gaps(total, target_R, min_gap=min_gap, max_gap=max_gap)

    # construire la liste des rectangles (chaque rectangle = (sx0, sx1, sy0, sy1))
    rects = []
    cur = 0
    if horizontal_long:
        for i in range(target_R):
            wseg = widths[i]
            seg_x0 = x0 + cur
            seg_x1 = seg_x0 + wseg - 1
            seg_y0 = y0
            seg_y1 = y1
            rects.append((seg_x0, seg_x1, seg_y0, seg_y1))
            cur += wseg
            if i < len(gaps):
                cur += gaps[i]
    else:
        for i in range(target_R):
            hseg = widths[i]
            seg_y0 = y0 + cur
            seg_y1 = seg_y0 + hseg - 1
            seg_x0 = x0
            seg_x1 = x1
            rects.append((seg_x0, seg_x1, seg_y0, seg_y1))
            cur += hseg
            if i < len(gaps):
                cur += gaps[i]

    # attribution round-robin des rectangles aux k couleurs
    color_rects = {ci: [] for ci in range(k)}
    for ridx, rect in enumerate(rects):
        c = ridx % k
        color_rects[c].append(rect)

    # construire les paths : concaténation des périmètres des rectangles assignés
    paths = {}
    for c in range(k):
        pts_all = []
        for rect in color_rects[c]:
            sx0, sx1, sy0, sy1 = rect
            pts = _perimeter_points(sx0, sx1, sy0, sy1)
            pts_all.extend(pts)
        paths[c] = pts_all

    return paths
    

def generate_rect_paths(n: int, m: int, k: int, margin: int = 2,
                        min_gap: int = 1, max_gap: int = 4,
                        allow_multiple_per_color: bool = True) -> Dict[int, List[Tuple[int, int]]]:
    """
    Génère des paths (périmètres rectangulaires intérieurs) pour une map n x m.
    - k : nombre de robots (2..4)
    - margin : marge au bord (par défaut 2)
    - min_gap / max_gap : espacement entre rectangles successifs (en cases)
    - allow_multiple_per_color : si True, on peut attribuer plusieurs rectangles à une même couleur.
    Retour : dictionnaire {color_idx: [(x,y), ...], ...} avec color_idx de 0 à k-1.
    """
    if k < 2 or k > 4:
        raise ValueError("k doit être entre 2 et 4 (inclus).")
    if n <= 2 * margin or m <= 2 * margin:
        raise ValueError("La map est trop petite pour la marge demandée.")

    x0 = margin
    x1 = m - 1 - margin
    y0 = margin
    y1 = n - 1 - margin

    width = x1 - x0 + 1
    height = y1 - y0 + 1

    horizontal_long = (width >= height)

    # helper pour calculer le nombre max possible de rectangles
    def max_possible_rects(total: int, min_gap: int):
        # chaque rectangle prend au moins 1 case, chaque gap au moins min_gap
        # pour R rectangles il faut total >= R + (R-1)*min_gap => R <= floor((total+min_gap)/(1+min_gap))
        return (total + min_gap) // (1 + min_gap)

    # on choisit le nombre de rectangles R
    if horizontal_long:
        total = width
    else:
        total = height

    max_rects = max_possible_rects(total, min_gap)
    # on vise jusqu'à 2*k rectangles si possible (deux par couleur), sinon on prend min(max_rects, k)
    if allow_multiple_per_color:
        target_R = min(max_rects, 2 * k)
        if target_R < k:
            # impossible d'allouer deux par couleur, on force au moins k si possible
            target_R = min(max_rects, k)
    else:
        target_R = min(max_rects, k)

    if target_R <= 0:
        raise ValueError("Dimension interne trop petite pour placer des rectangles avec les gaps demandés.")

    # allouer widths et gaps pour target_R rectangles le long de l'axe long
    widths, gaps = _allocate_widths_and_gaps(total, target_R, min_gap=min_gap, max_gap=max_gap)

    # construire la liste ordonnée des rectangles (chaque rect défini par x0,x1,y0,y1)
    rects = []
    cur = 0
    if horizontal_long:
        for i in range(target_R):
            wseg = widths[i]
            seg_x0 = x0 + cur
            seg_x1 = seg_x0 + wseg - 1
            seg_y0 = y0
            seg_y1 = y1
            rects.append((seg_x0, seg_x1, seg_y0, seg_y1))
            cur += wseg
            if i < len(gaps):
                cur += gaps[i]
    else:
        for i in range(target_R):
            hseg = widths[i]
            seg_y0 = y0 + cur
            seg_y1 = seg_y0 + hseg - 1
            seg_x0 = x0
            seg_x1 = x1
            rects.append((seg_x0, seg_x1, seg_y0, seg_y1))
            cur += hseg
            if i < len(gaps):
                cur += gaps[i]

    # attribuer les rectangles aux couleurs (0..k-1)
    # stratégie : round-robin sur les rectangles pour répartir équitablement
    color_rects: Dict[int, List[Tuple[int,int,int,int]]] = {ci: [] for ci in range(k)}
    for idx_rect, rect in enumerate(rects):
        color_idx = idx_rect % k  # round-robin
        color_rects[color_idx].append(rect)

    # construire les paths par couleur : concaténation des périmètres des rectangles dans l'ordre
    paths: Dict[int, List[Tuple[int, int]]] = {}
    for color_idx in range(k):
        pts_all: List[Tuple[int, int]] = []
        assigned = color_rects[color_idx]
        for rect in assigned:
            sx0, sx1, sy0, sy1 = rect
            pts = _perimeter_points(sx0, sx1, sy0, sy1)
            # on ajoute les points du rectangle. On ne relie pas les rectangles entre eux :
            # il y aura donc une discontinuité (c'est voulu; robot peut sauter entre rects si nécessaire).
            pts_all.extend(pts)
        paths[color_idx] = pts_all

    return paths



# ----------------- UI: TextBox simple pour Pygame -----------------
class TextBox:
    """Champ texte simple."""
    def __init__(self, rect: pygame.Rect, text: str = "", font=None):
        self.rect = rect
        self.text = text
        self.active = False
        self.font = font or pygame.font.SysFont("Arial", 16)
        self.color_inactive = (180, 180, 180)
        self.color_active = (80, 80, 80)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # n'accepter que les caractères imprimables
                if event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, surface):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        txt = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (self.rect.x + 4, self.rect.y + 6))


# ----------------- Classe principale modifiée -----------------
class PathListEditor:
    """
    Editeur de grille enrichi : permet saisir nombre de robots et dimensions,
    générer automatiquement les paths, éditer/corriger manuellement et valider.
    """
    def __init__(self, map_id=1, cell_size=20):
        # lecture initiale des dimensions depuis config
        try:
            self.map_w, self.map_h = load_map_size(map_id)
        except Exception:
            # fallback si le fichier config n'existe pas durant les tests
            self.map_w, self.map_h = 35, 30

        self.cell_size = cell_size

        pygame.init()
        self.panel_height = 100  # espace plus grand pour inputs
        self._init_screen()

        # couleurs
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.ORANGE = (255, 165, 0)
        self.GREEN = (0, 255, 0)
        self.VIOLET = (148, 0, 211)
        self.BG_PANEL = (230, 230, 230)

        self.color_map = {
            0: ("none", self.WHITE),
            1: ("blue", self.BLUE),
            2: ("red", self.RED),
            3: ("orange", self.ORANGE),
            4: ("green", self.GREEN),
            5: ("black", self.BLACK),
            6: ("violet", self.VIOLET),
        }

        # grille
        self.grid = [
            [0 for _ in range(self.map_w)] for _ in range(self.map_h)
        ]

        self.current_color_idx = 1
        self.mouse_button_held = None
        self.dragging_in_grid = False

        # boutons
        btn_width = 120
        btn_height = 36
        btn_x = self.map_w * self.cell_size - btn_width - 20
        btn_y = self.map_h * self.cell_size + (self.panel_height - btn_height) // 2
        self.validate_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        # bouton générer (pour inputs)
        gen_x = btn_x - (btn_width + 20)
        self.generate_rect = pygame.Rect(gen_x, btn_y, btn_width, btn_height)

        self.font = pygame.font.SysFont("Arial", 18, True)

        # palette
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

        # TextBoxes : nombre de robots et dimension W x H
        tb_w = 140
        tb_h = 28
        tb1_rect = pygame.Rect(20, self.map_h * self.cell_size + 8, tb_w, tb_h)
        tb2_rect = pygame.Rect(20 + tb_w + 10, self.map_h * self.cell_size + 8, tb_w, tb_h)
        self.tb_robots = TextBox(tb1_rect, text="2", font=self.font)
        self.tb_dim = TextBox(tb2_rect, text=f"{self.map_w}x{self.map_h}", font=self.font)

        # message d'erreur à afficher dans la console / panneau
        self.last_message = ""

        # appliquer listes prédéfinies si présentes
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
                self.apply_list(globals_dict[name], color_idx)

        self.running = True
        self.clock = pygame.time.Clock()

    def _init_screen(self):
        self.screen = pygame.display.set_mode(
            (self.map_w * self.cell_size, self.map_h * self.cell_size + self.panel_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Path List Editor (avec génération)")

    def apply_list(self, points, color_idx):
        """Colorie une liste de points."""
        if color_idx not in self.color_map:
            return
        for x, y in points:
            if 0 <= x < self.map_w and 0 <= y < self.map_h:
                self.grid[y][x] = color_idx

    def recreate_grid_and_window(self, new_w: int, new_h: int):
        """Redimensionne la grille et la fenêtre en conservant l'ancien contenu si possible."""
        old_w, old_h = self.map_w, self.map_h
        old_grid = self.grid
        self.map_w, self.map_h = new_w, new_h
        # nouveau grid vierge
        self.grid = [[0 for _ in range(self.map_w)] for _ in range(self.map_h)]
        # recopie partielle de l'ancien contenu (si compatible)
        for y in range(min(old_h, self.map_h)):
            for x in range(min(old_w, self.map_w)):
                self.grid[y][x] = old_grid[y][x]
        # réinitialise surface et position des boutons/textboxes
        self._init_screen()
        # repositionner validate/generate rectangles
        btn_width = 120
        btn_height = 36
        btn_x = self.map_w * self.cell_size - btn_width - 20
        btn_y = self.map_h * self.cell_size + (self.panel_height - btn_height) // 2
        self.validate_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        gen_x = btn_x - (btn_width + 20)
        self.generate_rect = pygame.Rect(gen_x, btn_y, btn_width, btn_height)
        # reposition palette and textboxes
        palette_indices = list(self.palette_rects.keys())
        box_size = 30
        spacing = 10
        start_x = 20
        center_y = self.map_h * self.cell_size + self.panel_height // 2
        top_y = center_y - box_size // 2
        for i, idx in enumerate(palette_indices):
            x = start_x + i * (box_size + spacing)
            self.palette_rects[idx] = pygame.Rect(x, top_y, box_size, box_size)
        tb_w = 140
        tb_h = 28
        self.tb_robots.rect = pygame.Rect(20, self.map_h * self.cell_size + 8, tb_w, tb_h)
        self.tb_dim.rect = pygame.Rect(20 + tb_w + 10, self.map_h * self.cell_size + 8, tb_w, tb_h)

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

        elif event.type == pygame.VIDEORESIZE:
            # redimensionnement manuel de la fenêtre : on ne change pas la map
            w, h = event.size
            pygame.display.set_mode((w, h), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # si clic sur valider
            if self.validate_rect.collidepoint(x, y):
                self.on_validate()
                return
            # si clic sur générer
            if self.generate_rect.collidepoint(x, y):
                self.on_generate()
                return
            # clic palette
            for idx, rect in self.palette_rects.items():
                if rect.collidepoint(x, y):
                    self.current_color_idx = idx
                    return
            # gérer textbox clicks
            self.tb_robots.handle_event(event)
            self.tb_dim.handle_event(event)
            # cliquer dans la grille pour peindre
            if y < self.map_h * self.cell_size:
                grid_x = x // self.cell_size
                grid_y = y // self.cell_size
                if 0 <= grid_x < self.map_w and 0 <= grid_y < self.map_h:
                    if event.button == 1:
                        self.grid[grid_y][grid_x] = self.current_color_idx
                        self.mouse_button_held = 1
                        self.dragging_in_grid = True
                    elif event.button == 3:
                        self.grid[grid_y][grid_x] = 0
                        self.mouse_button_held = 3
                        self.dragging_in_grid = True

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
                        else:
                            self.grid[grid_y][grid_x] = 0

        elif event.type == pygame.KEYDOWN:
            # propagation aux textboxes
            self.tb_robots.handle_event(event)
            self.tb_dim.handle_event(event)
            # raccourcis de palette
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
        # fond grille
        self.screen.fill(self.WHITE)
        # draw cells
        for y in range(self.map_h):
            for x in range(self.map_w):
                idx = self.grid[y][x]
                _, color = self.color_map[idx]
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                )
        # lignes de la grille
        for i in range(1, self.map_h):
            pygame.draw.line(self.screen, self.BLACK, (0, i * self.cell_size), (self.map_w * self.cell_size, i * self.cell_size))
        for j in range(1, self.map_w):
            pygame.draw.line(self.screen, self.BLACK, (j * self.cell_size, 0), (j * self.cell_size, self.map_h * self.cell_size))

        # panneau bas
        pygame.draw.rect(self.screen, self.BG_PANEL, pygame.Rect(0, self.map_h * self.cell_size, self.map_w * self.cell_size, self.panel_height))

        # palette
        for idx, rect in self.palette_rects.items():
            name, color = self.color_map[idx]
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, width=2)
            label = "E" if idx == 0 else str(idx)
            text = self.font.render(label, True, self.BLACK if idx != 5 else self.WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # boutons
        pygame.draw.rect(self.screen, (200, 200, 200), self.validate_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.validate_rect, width=2)
        txt = self.font.render("Valider", True, self.BLACK)
        txt_rect = txt.get_rect(center=self.validate_rect.center)
        self.screen.blit(txt, txt_rect)


        pygame.draw.rect(self.screen, (200, 200, 200), self.generate_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.generate_rect, width=2)
        txtg = self.font.render("Générer", True, self.BLACK)
        txtg_rect = txtg.get_rect(center=self.generate_rect.center)
        self.screen.blit(txtg, txtg_rect)

        # textboxes
        lbl1 = self.font.render("Robots (2..4) :", True, self.BLACK)
        self.screen.blit(lbl1, (20, self.map_h * self.cell_size - 2))
        self.tb_robots.draw(self.screen)

        lbl2 = self.font.render("Dimensions WxH (ex: 35x30) :", True, self.BLACK)
        self.screen.blit(lbl2, (20 + 140 + 10, self.map_h * self.cell_size - 2))
        self.tb_dim.draw(self.screen)

        # info couleur
        name, _ = self.color_map[self.current_color_idx]
        info_text = self.font.render(f"Couleur: {name}", True, self.BLACK)
        self.screen.blit(info_text, (10, self.map_h * self.cell_size + self.panel_height - 26))

        # message (erreur/info)
        msg = self.font.render(self.last_message, True, (180, 0, 0))
        self.screen.blit(msg, (20, self.map_h * self.cell_size + self.panel_height - 48))

        pygame.display.flip()

    def on_validate(self):
        """Imprime dans la console les listes de points par couleur (sauf eraser)."""
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

    def on_generate(self):
        """
        Lis les inputs (robots, dimensions), génère automatiquement les paths,
        redimensionne la fenêtre si besoin et applique les paths aux couleurs.
        """
        robots_txt = self.tb_robots.text.strip()
        dim_txt = self.tb_dim.text.strip()
        # parse robots
        try:
            k = int(robots_txt)
        except Exception:
            self.last_message = "Erreur: nombre de robots invalide."
            print(self.last_message)
            return
        if not (2 <= k <= 4):
            self.last_message = "Erreur: robots doit être entre 2 et 4."
            print(self.last_message)
            return
        # parse dimensions WxH
        try:
            w_str, h_str = dim_txt.lower().split("x")
            w = int(w_str)
            h = int(h_str)
        except Exception:
            self.last_message = "Erreur: dimensions invalides (format WxH)."
            print(self.last_message)
            return
        if w <= 6 or h <= 6:
            self.last_message = "Erreur: dimensions trop petites (min >6)."
            print(self.last_message)
            return

        # si dimension différente, recréer grille et window
        if (w, h) != (self.map_w, self.map_h):
            self.recreate_grid_and_window(w, h)

        # essayer de générer les paths
        try:
            paths = generate_rect_paths(n=self.map_h, m=self.map_w, k=k, margin=2, min_gap=1, max_gap=4, allow_multiple_per_color=True)
        except Exception as e:
            self.last_message = f"Erreur génération: {e}"
            print(self.last_message)
            return

        # vider la grille puis appliquer paths en couleurs 1..k
        self.grid = [[0 for _ in range(self.map_w)] for _ in range(self.map_h)]
        for idx, pts in paths.items():
            color_idx = (idx % 6) + 1  # choisit une couleur cyclique entre 1..6
            self.apply_list(pts, color_idx)

        self.last_message = f"Généré {len(paths)} paths pour {k} robots ({w}x{h})."
        print(self.last_message)


if __name__ == "__main__":
    editor = PathListEditor(map_id=1)
    editor.run()
