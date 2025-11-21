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

            print("hellooo: ", msg)
            print("agent_id ", self.agent_id)
            

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
        sleep(self.delay_to_moove)                
    

    def strategy(self):
        self.way_to_the_closest_point()
       
        for next_point in self.goal_list:
            self.moove(next_point)

        #print('goal_reached')

        lst = lists[self.agent_id]
        self.points_not_reached_yet = lst
        i = lst.index(next_point)

        for point in lst[i+1:]:
            self.moove(point)
            self.points_not_reached_yet.remove(point)
        print(self.points_not_reached_yet)

        if len(self.points_not_reached_yet)!=0:
            self.closest_point = self.where_closest_point()

            self.way_to_the_closest_point()
       
            for next_point in self.goal_list:
                self.moove(next_point)
            
            for point in self.points_not_reached_yet:
                        
                self.moove(point)
                self.points_not_reached_yet.remove(point)



    
         
             


            
            
         

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



