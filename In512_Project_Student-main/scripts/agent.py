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
        self.delay_to_moove = 0.2
        self.points_not_reached_yet = []
        self.claim_zone = []
        self.key_pos = []
        self.chest_pos = []
              
    def msg_cb(self): 
        """ Method used to handle incoming messages """
        while self.running:
            msg = self.network.receive()
            self.msg = msg
            if msg["header"] == MOVE:
                self.x, self.y =  msg["x"], msg["y"]
                print(self.x, self.y)
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

        # Enregistrer la position actuelle avant de bouger
        if not hasattr(self, 'previous_positions'):
            self.previous_positions = []
        self.previous_positions.append((self.x, self.y))

        sleep(self.delay_to_moove)
             
            
 
    def value_cell_val(self):
        self.network.send({"header": GET_DATA, "x": self.x, "y": self.y})
        time.sleep(0.1)
        cell_val = self.msg.get("cell_val")
        return cell_val
    
    def zone(self):
        if (self.x, self.y) in self.claim_zone:  # Enlever les parenthèses après claim_zone
            return True
        else:
            return False
        
    def new_zone(self, coord):
        x, y = coord
        if not hasattr(self, 'claim_zone'):
            self.claim_zone = []  # Initialisation si elle n'existe pas

        for dx in range(-2, 3):  # De -2 à +2 inclus
            for dy in range(-2, 3):  # De -2 à +2 inclus
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) not in self.claim_zone:  # Éviter les doublons
                    self.claim_zone.append((new_x, new_y))


        # Parcourir toutes les cases dans un carré de côté 5 (distance max de 2)
        for dx in range(-2, 3):  # De -2 à +2 inclus
            for dy in range(-2, 3):  # De -2 à +2 inclus
                new_x, new_y = x + dx, y + dy
                # Ajouter la case à la liste
                if (new_x, new_y) not in self.claim_zone:  # Éviter les doublons
                    self.claim_zone.append((new_x, new_y))



    def find(self, next_point):
        try:
            if self.zone() == True:
                return
            
            cell_val = self.value_cell_val()

            if cell_val not in [0.25, 0.3]:
                print("Valeur initiale non valide.")
                return False

            print(f"Détection {cell_val}, exploration des diagonales autour de cette case.")
            x0, y0 = self.x, self.y  # Position de départ
            DIAGONAL_MOVES = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

            for i in DIAGONAL_MOVES:
                self.moove((x0 + i[0], y0 + i[1]))
                val = self.value_cell_val()
                print(f"Valeur de la case {(x0 + i[0], y0 + i[1])} : {val}")

                if val == 0:
                    self.moove((x0, y0))  # Retour à la position initiale

                # Si on trouve une case 0.25 ou 0.3
                if val in [0.25, 0.3]:
                    if i == (1, 1):  # Bas-droite
                        print(f"Piste en bas-droite ! Déplacement vers (x0+1, y0) puis (x0+2, y0+1)")
                        self.moove((x0 + 1, y0))
                        self.moove((x0 + 2, y0 + 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return 
                    elif i == (1, -1):  # Haut-droite
                        print(f"Piste en haut-droite ! Déplacement vers (x0+1, y0) puis (x0+2, y0-1)")
                        self.moove((x0 + 1, y0))
                        self.moove((x0 + 2, y0 - 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return 
                    elif i == (-1, -1):  # Haut-gauche
                        print(f"Piste en haut-gauche ! Déplacement vers (x0-1, y0) puis (x0-2, y0-1)")
                        self.moove((x0 - 1, y0))
                        self.moove((x0 - 2, y0 - 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return 
                    elif i == (-1, 1):  # Bas-gauche
                        print(f"Piste en bas-gauche ! Déplacement vers (x0-1, y0) puis (x0-2, y0+1)")
                        self.moove((x0 - 1, y0))
                        self.moove((x0 - 2, y0 + 1))
                        print("Valeur de la case finale :", self.value_cell_val())
                        return 

                # Si on trouve une case 0.5 ou 0.6
                if val in [0.5, 0.6]:
                    print(f"Case de valeur {val} détectée. Exploration des cases adjacentes...")
                    x1, y1 = self.x, self.y
                    # Définition des 8 directions adjacentes (4 orthogonales + 4 diagonales)
                    ADJACENT_MOVES = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

                    for move in ADJACENT_MOVES:
                        new_x, new_y = x1 + move[0], y1 + move[1]
                        self.moove((new_x, new_y))
                        adjacent_val = self.value_cell_val()
                        print(f"Valeur de la case adjacente {(new_x, new_y)} : {adjacent_val}")

                        if adjacent_val == 1:
                            print(f"Objet trouvé en {(new_x, new_y)} !")
                            self.new_zone((new_x, new_y))
                            #On claim la zone
                            return 

            print("Aucune piste valide trouvée.")
            return 

        except Exception as e:
            print(f"Erreur find(): {e}")
            return False
















    def strategy(self):
        if not self.points_not_reached_yet:
            self.points_not_reached_yet = lists[self.agent_id].copy()

        while self.points_not_reached_yet:
            self.closest_point = self.where_closest_point(self.points_not_reached_yet)
            self.way_to_the_closest_point()

            for next_point in self.goal_list:
                self.find(next_point)
                self.moove(next_point)
                

                if next_point in self.points_not_reached_yet:
                    self.points_not_reached_yet.remove(next_point)
                print("Points restants :", self.points_not_reached_yet)





    
         
             


            
            
         

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
