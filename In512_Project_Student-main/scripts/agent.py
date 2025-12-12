__author__ = "Aybuke Ozturk Suri, Johvany Gustave"
__copyright__ = "Copyright 2023, IN512, IPSA 2024"
__credits__ = ["Aybuke Ozturk Suri", "Johvany Gustave"]
__license__ = "Apache License 2.0"
__version__ = "1.0.0"

from network import Network
from my_constants import *
from threading import Thread
import numpy as np
from time import sleep
import time

import heapq
import math

class Agent:
    """Class that implements the behaviour of each agent based on their perception and communication with other agents."""

    def __init__(self, server_ip):
        # Initialisation des mouvements possibles
        self.moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

        # Initialisation des attributs de base
        self.network = Network(server_ip=server_ip)
        self.agent_id = self.network.id
        self.running = True
        self.msg = {}
        self.delay_to_moove = 0.05

        # Initialisation des attributs d'état et de suivi
        self.all_keys_found = set()
        self.all_boxes_found = set()
        self.has_key = False
        self.has_opened_box = False
        self.nb_objects_found = 0
        self.key_pos = []
        self.chess_pos = []
        self.claim_zone = []
        self.last_item_info = None
        self.nb_agent_expected = 0
        self.nb_agent_connected = 0
        self.x, self.y = 0, 0
        self.w, self.h = 0, 0
        self.path_map = {}
        self.closest_point = None
        self.goal_list = []
        #self.delay_to_moove = 0.5
        self.points_not_reached_yet = []
        self.detect=False
        self.claim_zone = []
        self.key_pos = []
        self.chest_pos = []

        # Envoi initial pour récupérer les données de l'environnement
        self.network.send({"header": GET_DATA})
        env_conf = self.network.receive()
        self.x, self.y = env_conf["x"], env_conf["y"]
        self.w, self.h = env_conf["w"], env_conf["h"]

        # Lancement du thread de réception des messages
        Thread(target=self.msg_cb, daemon=True).start()

        # Attente de la connexion des agents
        self.wait_for_connected_agent()
        self.path_map = self.select_path_map()

        # Vérification que la liste de points existe pour cet agent
        if self.agent_id not in self.path_map or not self.path_map.get(self.agent_id):
            print(f"Erreur : Aucune liste de points trouvée pour l'agent {self.agent_id}. Utilisation d'une liste par défaut.")
            self.path_map[self.agent_id] = [(self.x + 1, self.y)]  # Liste par défaut avec un point proche

        self.closest_point = self.where_closest_point(self.path_map.get(self.agent_id, []))
        if self.closest_point is None:
            self.closest_point = (self.x + 1, self.y)  # Point par défaut légèrement décalé

    def has_found_own_items(self):
        """Retourne True si la clé et le coffre propres à l'agent ont été trouvés."""
        return len(self.key_pos) > 0 and len(self.chess_pos) > 0

    def select_path_map(self):
        """Choisit le dictionnaire de path en fonction du nombre d'agents attendus."""
        if self.nb_agent_expected == 2:
            return list_for_2
        if self.nb_agent_expected == 3:
            return list_for_3
        if self.nb_agent_expected == 4:
            # Vérifiez les clés disponibles dans list_for_4
            if self.agent_id in list_for_4:
                return {self.agent_id: list_for_4[self.agent_id]}
            else:
                print(f"Erreur : Aucune liste pour l'agent {self.agent_id} dans list_for_4.")
                return {self.agent_id: [(self.x + 1, self.y)]}  # Liste par défaut avec un point proche
        return {self.agent_id: [(self.x + 1, self.y)]}

    def all_items_found(self):
        """Vrai si toutes clés+coffres (2 par agent) ont été découverts par au moins un agent."""
        if self.nb_agent_expected <= 0:
            return False
        return (len(self.all_keys_found) + len(self.all_boxes_found)) >= 2 * self.nb_agent_expected

    def move_to(self, target):
        """Déplacement pas-à-pas vers une cible, sans optimisations."""
        tx, ty = target
        while (self.x, self.y) != (tx, ty):
            cx, cy = self.x, self.y
            nx = cx + (1 if tx > cx else -1 if tx < cx else 0)
            ny = cy + (1 if ty > cy else -1 if ty < cy else 0)
            self.moove((nx, ny))

    def in_own_items(self, position):
        """True si la position correspond à mon coffre ou ma clé connue."""
        return position in self.key_pos or position in self.chess_pos

    def msg_cb(self):
        """Method used to handle incoming messages"""
        while self.running:
            msg = self.network.receive()
            if msg is None:
                continue
            self.msg = msg
            try:
                if msg["header"] == MOVE:
                    self.x, self.y = msg["x"], msg["y"]
                elif msg["header"] == GET_NB_AGENTS:
                    self.nb_agent_expected = msg["nb_agents"]
                elif msg["header"] == GET_NB_CONNECTED_AGENTS:
                    self.nb_agent_connected = msg["nb_connected_agents"]
                elif msg["header"] == GET_ITEM_OWNER:
                    self.last_item_info = msg
                    owner = msg.get("owner")
                    typ = msg.get("type")
                    if owner == self.agent_id:
                        if typ == KEY_TYPE:
                            self.has_key = True
                        elif typ == BOX_TYPE and self.has_key:
                            self.has_opened_box = True
                elif msg["header"] == "CLAIMED_ZONE":
                    position = msg.get("position")
                    owner = msg.get("owner")
                    if position and position not in self.claim_zone:
                        self.new_zone(position)
                elif msg["header"] == "KEY_POS":
                    owner, position = msg["value"]
                    if owner == self.agent_id and position not in self.key_pos:
                        self.key_pos.append(position)
                    pos_t = tuple(position)
                    before = len(self.all_keys_found) + len(self.all_boxes_found)
                    self.all_keys_found.add(pos_t)
                    after = len(self.all_keys_found) + len(self.all_boxes_found)
                    if after > before:
                        self.nb_objects_found += 1
                elif msg["header"] == "CHESS_POS":
                    owner, position = msg["value"]
                    if owner == self.agent_id and position not in self.chess_pos:
                        self.chess_pos.append(position)
                    pos_t = tuple(position)
                    before = len(self.all_keys_found) + len(self.all_boxes_found)
                    self.all_boxes_found.add(pos_t)
                    after = len(self.all_keys_found) + len(self.all_boxes_found)
                    if after > before:
                        self.nb_objects_found += 1
                elif msg["header"] == BROADCAST_MSG:
                    obj_type = msg.get("Msg type")
                    position = msg.get("position")
                    owner = msg.get("owner")
                    if position is not None:
                        position = tuple(position)
                    if obj_type == KEY_DISCOVERED and position:
                        before = len(self.all_keys_found) + len(self.all_boxes_found)
                        self.all_keys_found.add(position)
                        after = len(self.all_keys_found) + len(self.all_boxes_found)
                        if after > before:
                            self.nb_objects_found += 1
                    elif obj_type == BOX_DISCOVERED and position:
                        before = len(self.all_keys_found) + len(self.all_boxes_found)
                        self.all_boxes_found.add(position)
                        after = len(self.all_keys_found) + len(self.all_boxes_found)
                        if after > before:
                            self.nb_objects_found += 1
                    if owner == self.agent_id:
                        if obj_type == KEY_DISCOVERED and position and position not in self.key_pos:
                            self.key_pos.append(position)
                        elif obj_type == BOX_DISCOVERED and position and position not in self.chess_pos:
                            self.chess_pos.append(position)
            except Exception as e:
                print(f"Erreur dans msg_cb: {e}")

    def wait_for_connected_agent(self):
        self.network.send({"header": GET_NB_AGENTS})
        check_conn_agent = True
        while check_conn_agent:
            if self.nb_agent_expected == self.nb_agent_connected:
                print(f"Agent {self.agent_id} connecté!")
                check_conn_agent = False

    def where_closest_point(self, lst=None):
        """Trouve le point le plus proche dans la liste, en ignorant la position actuelle de l'agent."""
        if lst is None:
            lst = self.path_map.get(self.agent_id, [])
        if not lst:
            print(f"Aucun point dans la liste pour l'agent {self.agent_id}. Retour à un point proche.")
            return (self.x + 1, self.y)  # Retourne un point proche si la liste est vide

        d_min = float("inf")
        best = None
        for x, y in lst:
            if (x, y) == (self.x, self.y):
                continue  # Ignorer la position actuelle de l'agent
            dist = (x - self.x)**2 + (y - self.y)**2
            if dist < d_min:
                d_min = dist
                best = (x, y)

        if best is None:
            print(f"Aucun point trouvé dans la liste (hors position actuelle) pour l'agent {self.agent_id}. Retour à un point proche.")
            return (self.x + 1, self.y)  # Retourne un point proche si aucun autre point n'est trouvé

        print(f"Point le plus proche trouvé pour l'agent {self.agent_id} : {best}")
        return best

    def way_to_the_closest_point(self):
        """Calcule le chemin vers le point le plus proche."""
        if self.closest_point is None:
            print("Erreur : self.closest_point est None. Utilisation d'un point proche.")
            self.closest_point = (self.x + 1, self.y)
        print(f"Déplacement vers le point le plus proche : {self.closest_point}")
        x_goal, y_goal = self.closest_point
        x_current, y_current = self.x, self.y
        self.goal_list = []
        while (x_current, y_current) != (x_goal, y_goal):
            if x_current > x_goal:
                x_current -= 1
            elif x_current < x_goal:
                x_current += 1
            if y_current > y_goal:
                y_current -= 1
            elif y_current < y_goal:
                y_current += 1
            self.goal_list.append((x_current, y_current))

    def moove(self, next_point):

        if not hasattr(self, 'previous_positions'):
            self.previous_positions = []
        self.previous_positions.append((self.x, self.y))
        
        x_next, y_next = next_point
        dx = x_next - self.x
        dy = y_next - self.y
        move_vec = (dx, dy)
        if move_vec in self.moves:
            next_move = self.moves.index(move_vec)
        else:
            next_move = STAND
        cmds = {
            "header": MOVE,
            "direction": next_move,
        }
        self.network.send(cmds)
        
        sleep(self.delay_to_moove)

        val = self.value_cell_val()
        if not hasattr(self, "known_map"):
            self.known_map = {}
        
        self.known_map[(self.x, self.y)] = val
             

    def request_item_info(self, x, y, timeout=2.0):
        """Envoie une requête GET_ITEM_OWNER et attend la réponse."""
        self.last_item_info = None
        self.network.send({"header": GET_ITEM_OWNER, "x": x, "y": y})
        start = time.time()
        while time.time() - start < timeout:
            if self.last_item_info is not None:
                return self.last_item_info
            sleep(0.01)
        print(f"Timeout lors de la récupération des infos de l'objet ({x}, {y})")
        return None

    def check_and_claim_object(self, new_x, new_y):
        """Identifie l'objet trouvé et met à jour les positions connues."""
        position = (new_x, new_y)
        item_info = self.request_item_info(new_x, new_y)
        if not item_info:
            return False
        item_owner = item_info.get("item_owner", item_info.get("owner"))
        item_type = item_info.get("item_type", item_info.get("type"))
        if item_type == KEY_TYPE:
            obj_type = KEY_DISCOVERED
        elif item_type == BOX_TYPE:
            obj_type = BOX_DISCOVERED
        else:
            obj_type = KEY_DISCOVERED
        print(f"Type: {obj_type}, Position: {position}, Owner: {item_owner}")
        self.new_zone(position)
        if position not in self.claim_zone:
            self.claim_zone.append(position)
        if item_owner == self.agent_id:
            if obj_type == KEY_DISCOVERED:
                if position not in self.key_pos:
                    self.key_pos.append(position)
            elif obj_type == BOX_DISCOVERED:
                if position not in self.chess_pos:
                    self.chess_pos.append(position)
        else:
            print(f"L'objet en {position} appartient à l'agent {item_owner}, diffusion...")
        before = len(self.all_keys_found) + len(self.all_boxes_found)
        if obj_type == KEY_DISCOVERED:
            self.all_keys_found.add(position)
        elif obj_type == BOX_DISCOVERED:
            self.all_boxes_found.add(position)
        after = len(self.all_keys_found) + len(self.all_boxes_found)
        if after > before:
            self.nb_objects_found += 1
        self.network.send({
            "header": BROADCAST_MSG,
            "Msg type": obj_type,
            "position": position,
            "owner": item_owner,
            "type": item_type
        })
        self.network.send({
            "header": "CLAIMED_ZONE",
            "position": position,
            "owner": item_owner
        })
        return True


        
            
    def search_around(self, x_center, y_center, line_points):
        """Cherche la valeur 1 dans les cases autour de (x_center, y_center) en excluant les points de la ligne déjà visitée."""
        # Créer une liste de tous les points autour en formant un chemin continu
        all_around_points = [
            (x_center - 2, y_center - 2), (x_center - 1, y_center - 2), (x_center, y_center - 2),
            (x_center + 1, y_center - 2), (x_center + 2, y_center - 2),
            (x_center + 2, y_center - 1), (x_center + 2, y_center),
            (x_center + 2, y_center + 1), (x_center + 2, y_center + 2),
            (x_center + 1, y_center + 2), (x_center, y_center + 2),
            (x_center - 1, y_center + 2), (x_center - 2, y_center + 2),
            (x_center - 2, y_center + 1), (x_center - 2, y_center),
            (x_center - 2, y_center - 1)
        ]

        # Retirer les points qui sont sur la ligne déjà visitée
        filtered_points = [point for point in all_around_points if point not in line_points]

        #print(f"Points à explorer : {filtered_points}")

        # Explorer les points restants
        while filtered_points:
            x, y = filtered_points[0]
            self.moove((x, y))
            self.network.send({"header": GET_DATA, "x": x, "y": y})
            time.sleep(0.1)
            if hasattr(self, 'msg') and self.msg.get("header") == GET_DATA:
                neighbor_val = self.msg.get("cell_val", None)
                if neighbor_val == 1:
                    #print(f"Objet trouvé à (x={x}, y={y}) !")
                    return True
            filtered_points.pop(0)
            #print(f"Points restants : {filtered_points}")

        return False

 
    def value_cell_val(self):
        """Récupère la valeur de la cellule actuelle."""
        self.network.send({"header": GET_DATA, "x": self.x, "y": self.y})
        time.sleep(0.1)
        cell_val = self.msg.get("cell_val")
        return cell_val

    def zone(self):
        """Vérifie si la position actuelle est dans une zone claimée."""
        return (self.x, self.y) in self.claim_zone

    def new_zone(self, coord):
        """Ajoute une nouvelle zone claimée autour de la position donnée."""
        x, y = coord
        if not hasattr(self, 'claim_zone'):
            self.claim_zone = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) not in self.claim_zone:
                    self.claim_zone.append((new_x, new_y))

    def find(self, next_point):
        """Explore la cellule et les alentours pour trouver des objets."""
        try:
            if self.zone():
                return
            cell_val = self.value_cell_val()
            if cell_val not in [0.25, 0.3]:
                return False
            print(f"Détection {cell_val}, exploration des diagonales autour de cette case.")
            x0, y0 = self.x, self.y
            DIAGONAL_MOVES = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
            for i in DIAGONAL_MOVES:
                self.moove((x0 + i[0], y0 + i[1]))
                val = self.value_cell_val()
                print(f"Valeur de la case {(x0 + i[0], y0 + i[1])} : {val}")
                if val == 0:
                    self.moove((x0, y0))
                if val in [0.25, 0.3]:
                    if i == (1, 1):
                        print(f"Piste en bas-droite ! Déplacement vers (x0+1, y0) puis (x0+2, y0+1)")
                        self.moove((x0 + 1, y0))
                        self.moove((x0 + 2, y0 + 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return
                    elif i == (1, -1):
                        print(f"Piste en haut-droite ! Déplacement vers (x0+1, y0) puis (x0+2, y0-1)")
                        self.moove((x0 + 1, y0))
                        self.moove((x0 + 2, y0 - 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return
                    elif i == (-1, -1):
                        print(f"Piste en haut-gauche ! Déplacement vers (x0-1, y0) puis (x0-2, y0-1)")
                        self.moove((x0 - 1, y0))
                        self.moove((x0 - 2, y0 - 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return
                    elif i == (-1, 1):
                        print(f"Piste en bas-gauche ! Déplacement vers (x0-1, y0) puis (x0-2, y0+1)")
                        self.moove((x0 - 1, y0))
                        self.moove((x0 - 2, y0 + 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return
                if val in [0.5, 0.6]:
                    print(f"Case de valeur {val} détectée. Exploration des cases adjacentes...")
                    x1, y1 = self.x, self.y
                    ADJACENT_MOVES = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
                    for move in ADJACENT_MOVES:
                        new_x, new_y = x1 + move[0], y1 + move[1]
                        self.moove((new_x, new_y))
                        adjacent_val = self.value_cell_val()
                        print(f"Valeur de la case adjacente {(new_x, new_y)} : {adjacent_val}")
                        if adjacent_val == 1:
                            print(f"Objet trouvé en {(new_x, new_y)} !")
                            self.new_zone((new_x, new_y))
                            self.check_and_claim_object(new_x, new_y)
                            if self.chess_pos and (new_x, new_y) in self.chess_pos and not self.has_key:
                                print("Coffre trouvé sans la clé : je continue l'exploration, retour à la case précédente.")
                                self.moove((x0, y0))
                                return
                            return
            print("Aucune piste valide trouvée.")
            return
        except Exception as e:
            print(f"Erreur find(): {e}")
            return False
        
    def wall_detect(self):
        cell_val = self.value_cell_val()
        if cell_val==0.35: #zone du mur
            self.moove(self.previous_positions.pop()) #recule 
            self.previous_positions.pop()
            return True
        return False

    def strategy(self):
        """Stratégie principale de l'agent."""
        if not hasattr(self, 'key_pos'):
            self.key_pos = []
        if not hasattr(self, 'chess_pos'):
            self.chess_pos = []

        if self.agent_id not in self.path_map or not self.path_map[self.agent_id]:
            print(f"Erreur : Aucune liste de points à explorer pour l'agent {self.agent_id}. Utilisation d'une liste par défaut.")
            self.path_map[self.agent_id] = [(self.x + 1, self.y)]

        self.points_not_reached_yet = self.path_map[self.agent_id].copy()
        print(f"Points à explorer pour l'agent {self.agent_id} : {self.points_not_reached_yet}")

        while True:
            if not self.points_not_reached_yet:
                print(f"Aucun point restant à explorer pour l'agent {self.agent_id}.")
                if self.all_items_found():
                    print("Tous les objets ont été trouvés.")
                    if not self.has_key and self.key_pos:
                        print(f"Déplacement vers la clé en {self.key_pos[0]}")
                        self.move_to(self.key_pos[0])
                        self.check_and_claim_object(self.x, self.y)
                        continue
                    if self.has_key and not self.has_opened_box and self.chess_pos:
                        print(f"Déplacement vers le coffre en {self.chess_pos[0]}")
                        self.move_to(self.chess_pos[0])
                        self.check_and_claim_object(self.x, self.y)
                        if self.has_opened_box:
                            print("Coffre ouvert, arrêt de l'exploration.")
                            break
                    if self.has_found_own_items():
                        print("Clé et coffre trouvés, arrêt de l'exploration.")
                        break
                else:
                    self.points_not_reached_yet = self.path_map[self.agent_id].copy()
                    if not self.points_not_reached_yet:
                        print(f"Aucun point à explorer pour l'agent {self.agent_id}. Utilisation d'une liste par défaut.")
                        self.points_not_reached_yet = [(self.x + 1, self.y)]
                        print(f"Chemin vers le point le plus proche : {self.goal_list}")


            self.closest_point = self.where_closest_point(self.points_not_reached_yet)
            if self.closest_point == (self.x, self.y):
                print(f"Le point le plus proche est la position actuelle pour l'agent {self.agent_id}. Recherche d'un autre point.")

            self.way_to_the_closest_point()
            for next_point in self.goal_list:
                print(f"Déplacement vers le point {next_point}")
                self.find(next_point)
                self.detect=self.wall_detect()
                if not self.detect:
                    self.moove(next_point)
                n=0
                while self.detect:
                    print("JJJJJJj",n)
                    self.pathstar=self.Astar(next_point)
                    for movestar in self.pathstar:
                        self.moove(movestar)
                        #self.find(next_point)
                        self.detect=self.wall_detect()

                        if self.detect:
                            while self.wall_detect():
                                continue
                            break
                    if len(self.pathstar)==0 or n==3:
                        self.detect=False
                    
                    n=n+1
                if next_point in self.points_not_reached_yet:
                    self.points_not_reached_yet.remove(next_point)

            if len(self.points_not_reached_yet) == 0:
                print("Position clé", self.key_pos)
                print("Position coffre:", self.chess_pos)
                print("Claimed zone :", self.claim_zone)
                print("Nombre d'objets trouvés :", self.nb_objects_found)


    

    def Astar(self, goal):
        
        start = (self.x, self.y)
        goal = tuple(goal)

        if start == goal:
            return []

        # Création carte interne
        if not hasattr(self, "known_map"):
            self.known_map = {}

        # Directions possibles
        neighbors = [
            (-1, 0), (1, 0),
            (0, -1), (0, 1),
            (-1, -1), (-1, 1),
            (1, -1), (1, 1)
        ]

        def h(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        open = []
        heapq.heappush(open, (h(start, goal), 0, start))
        came_from = {}
        g_score = {start: 0}
        closed = set()

        while open:
            f, g, current = heapq.heappop(open)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                path = []
                node = goal
                while node != start:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                return path

            cx, cy = current

            for dx, dy in neighbors:
                nx, ny = cx + dx, cy + dy

                # limites monde
                if nx < 0 or ny < 0 or nx >= self.w or ny >= self.h:
                    continue

                cell = self.known_map.get((nx, ny), "unknown")

                # unknown → considéré libre
                if cell == 0.35:  # obstacle connu
                    continue

                tentative_g = g + math.hypot(dx, dy)

                if tentative_g < g_score.get((nx, ny), float("inf")):
                    g_score[(nx, ny)] = tentative_g
                    came_from[(nx, ny)] = current
                    f_score = tentative_g + h((nx, ny), goal)
                    heapq.heappush(open, (f_score, tentative_g, (nx, ny)))

        return []  


if __name__ == "__main__":
    from random import randint
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server_ip", help="Ip address of the server", type=str, default="localhost")
    args = parser.parse_args()
    agent = Agent(args.server_ip)
    agent.strategy()
    try:
        while True:
            cmds = {"header": int(input("0 <-> Broadcast msg\n1 <-> Get data\n2 <-> Move\n3 <-> Get nb connected agents\n4 <-> Get nb agents\n5 <-> Get item owner\n"))}
            if cmds["header"] == BROADCAST_MSG:
                cmds["Msg type"] = int(input("1 <-> Key discovered\n2 <-> Box discovered\n3 <-> Completed\n"))
                cmds["position"] = (agent.x, agent.y)
                cmds["owner"] = randint(0, 3)
            elif cmds["header"] == MOVE:
                cmds["direction"] = int(input("0 <-> Stand\n1 <-> Left\n2 <-> Right\n3 <-> Up\n4 <-> Down\n5 <-> UL\n6 <-> UR\n7 <-> DL\n8 <-> DR\n"))
            agent.network.send(cmds)
    except KeyboardInterrupt:
        pass
