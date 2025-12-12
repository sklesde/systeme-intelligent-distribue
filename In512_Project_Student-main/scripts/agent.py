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
    """ Class that implements the behaviour of each agent based on their perception and communication with other agents """
    def __init__(self, server_ip):
        #TODO: DEINE YOUR ATTRIBUTES HERE
        self.moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        
        #DO NOT TOUCH THE FOLLOWING INSTRUCTIONS
        self.network = Network(server_ip=server_ip)
        self.agent_id = self.network.id
        self.running = True
        self.network.send({"header": GET_DATA})
        self.msg = {}
        env_conf = self.network.receive()
        self.nb_agent_expected = 0
        self.nb_agent_connected = 0
        self.x, self.y = env_conf["x"], env_conf["y"]   #initial agent position
        self.w, self.h = env_conf["w"], env_conf["h"]   #environment dimensions
        cell_val = env_conf["cell_val"] #value of the cell the agent is located in
        print(cell_val)
        Thread(target=self.msg_cb, daemon=True).start()
        print("hello")
        self.wait_for_connected_agent()
        self.closest_point = self.where_closest_point()
        self.goal_list = []
        self.delay_to_moove = 0.5
        self.points_not_reached_yet = []
        self.detect=False
              
    def msg_cb(self): 
        """ Method used to handle incoming messages """
        while self.running:
            msg = self.network.receive()
            self.msg = msg
            if msg["header"] == MOVE:
                self.x, self.y =  msg["x"], msg["y"]
                #print(self.x, self.y)
            elif msg["header"] == GET_NB_AGENTS:
                self.nb_agent_expected = msg["nb_agents"]
            elif msg["header"] == GET_NB_CONNECTED_AGENTS:
                self.nb_agent_connected = msg["nb_connected_agents"]

            #print("position: ", msg)
            #print("type clée msg", msg["cell_value"])
            #print("agent_id ", self.agent_id)
            

    def wait_for_connected_agent(self):
        self.network.send({"header": GET_NB_AGENTS})
        check_conn_agent = True
        while check_conn_agent:
            if self.nb_agent_expected == self.nb_agent_connected:
                print("both connected!")
                check_conn_agent = False
#_________________________________________________#   
    def test_de_mouvement(self):
        for i in range(30):
            next_move = DOWN
            cmds={"header":MOVE,
                "direction":next_move
                }
            
            self.network.send(cmds)
            sleep(0.5)    
    
    def where_closest_point(self, lst=None):
        # Si aucun argument n'est donné → on prend la liste correspondant à l'agent
        if lst is None:
            lst = lists[self.agent_id]

        # Trouve le point le plus proche dans lst
        d_min = float("inf")
        best = None

        for x, y in lst:
            dist = (x - self.x)**2 + (y - self.y)**2  # distance sans sqrt
            if dist < d_min:
                d_min = dist
                best = (x, y)

        return best

        

    def way_to_the_closest_point(self):
        x_goal, y_goal = self.closest_point
        x_current, y_current = self.x, self.y
        self.goal_list = []

        while (x_current, y_current ) != (x_goal, y_goal):
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
        print("caca",len(self.previous_positions),self.previous_positions)
        
        
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

        # Enregistrer la position actuelle avant de bouger
        

        val = self.value_cell_val()
        if not hasattr(self, "known_map"):
            self.known_map = {}
        
        self.known_map[(self.x, self.y)] = val
             
            
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
        self.network.send({"header": GET_DATA, "x": self.x, "y": self.y})
        time.sleep(0.1)
        cell_val = self.msg.get("cell_val")
        return cell_val

    def find(self, next_point):
        """Détecte les valeurs 0.3 ou 0.25 et cherche la case de valeur 1 dans la direction du déplacement."""
        try:
            # 1. Récupérer la valeur de la case actuelle via la fonction dédiée
            cell_val = self.value_cell_val()
            if cell_val is None:
                #print("Aucune valeur trouvée sur cette case.")
                return False

            #print(f"Valeur de la case actuelle : {cell_val}")

            # 2. Si la valeur est 0.25 ou 0.3 → déclenche la recherche
            if cell_val in [0.25, 0.3]:
                #print(f"Case de valeur {cell_val} détectée, recherche de la case 1...")

                x_back, y_back = self.x, self.y
                dx = next_point[0] - x_back
                dy = next_point[1] - y_back
                line_points = []

                # Exemple pour direction droite → peut être adapté ensuite
                if dx == 1 and dy == 0:
                    print("Direction : Droite")

                    # Ligne verticale parallèle à droite
                    for i in range(-2, 3):
                        check_x = x_back + 2
                        check_y = y_back + i
                        self.moove((check_x, check_y))
                        line_points.append((check_x, check_y))

                        # Lecture de la valeur
                        val = self.value_cell_val()
                        #print(f"Test cellule ({check_x}, {check_y}) = {val}")

                        if val == 1:
                            print("Objet trouvé !")
                            return True

                else:
                    print("Direction non gérée pour le moment.")

                # 3. Recherche dans les alentours si la ligne n'a rien trouvé
                print("Recherche autour…")
                if self.search_around(x_back, y_back, line_points):
                    return True

                #print("Aucune case de valeur 1 trouvée.")
                return False

            return False

        except Exception as e:
            print(f"Erreur dans find(): {e}")
            return False
        
    def wall_detect(self):
        cell_val = self.value_cell_val()

        print("valeru celle", cell_val)
        if cell_val==0.35: #zone du mur
            self.moove(self.previous_positions.pop()) #recule 
            self.previous_positions.pop()
            

            return True
        return False
    

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


    def strategy(self):
        
        if not self.points_not_reached_yet:
            self.points_not_reached_yet = lists[self.agent_id].copy()

        while self.points_not_reached_yet:
            
            self.closest_point = self.where_closest_point(self.points_not_reached_yet)
            self.way_to_the_closest_point()

            for next_point in self.goal_list:

                print("analyse")
                #self.find(next_point)
                self.detect=self.wall_detect()
                if not self.detect:
                    print("ok, je bouge")
                    self.moove(next_point)

                while self.detect:
                    print("mur détecté")
                    self.pathstar=self.Astar(next_point)
                    for movestar in self.pathstar:
                        print("hhhh",self.pathstar)
                        self.moove(movestar)
                        self.detect=self.wall_detect()

                        if self.detect:
                            while self.wall_detect():
                                continue
                            break
                        
                    if len(self.pathstar)==0:
                        self.detect=False
                        
                    
                if next_point in self.points_not_reached_yet:
                    self.points_not_reached_yet.remove(next_point)

                #print("Points restants :", self.points_not_reached_yet)
           

    #TODO: CREATE YOUR METHODS HERE...

            
 
if __name__ == "__main__":
    from random import randint
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server_ip", help="Ip address of the server", type=str, default="localhost")
    args = parser.parse_args()

    agent = Agent(args.server_ip)
    #Our part
    #agent.test_de_mouvement() # This is a test to see how the robots works
    agent.strategy()
    try:    #Manual control test0
        while True:
            cmds = {"header": int(input("0 <-> Broadcast msg\n1 <-> Get data\n2 <-> Move\n3 <-> Get nb connected agents\n4 <-> Get nb agents\n5 <-> Get item owner\n"))}
            if cmds["header"] == BROADCAST_MSG:
                cmds["Msg type"] = int(input("1 <-> Key discovered\n2 <-> Box discovered\n3 <-> Completed\n"))
                cmds["position"] = (agent.x, agent.y)
                cmds["owner"] = randint(0,3) # TODO: specify the owner of the item
            elif cmds["header"] == MOVE:
                cmds["direction"] = int(input("0 <-> Stand\n1 <-> Left\n2 <-> Right\n3 <-> Up\n4 <-> Down\n5 <-> UL\n6 <-> UR\n7 <-> DL\n8 <-> DR\n"))
            agent.network.send(cmds)
    except KeyboardInterrupt:
    
        pass
# it is always the same location of the agent first location
