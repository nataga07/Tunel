# -*- coding: utf-8 -*-

"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 10

class Monitor():
    def __init__(self):
        self.car_tunnel_NORTH = Value('i',0) #Num de coches en el norte que estan dentro del tunel y van hacia el sur
        self.car_tunnel_SOUTH = Value('i',0) #Num de coches en el sur que  estan dentro del tunel y van hacia el norte
        self.mutex = Lock()
        self.sem_NORTH = Condition(self.mutex) #Semaforo de los coches que vienen en el norte
        self.sem_SOUTH = Condition(self.mutex) #Semaforo de los coches que vienen en el sur

    def no_cars_NORTH(self): #No hay coches dentro del tunel que vengan del NORTE
        return self.car_tunnel_NORTH.value == 0
   
    def no_cars_SOUTH(self): #No hay coches dentro del tunel que vengan del SUR
        return self.car_tunnel_SOUTH.value == 0

    """
    Un coche del Sur quiere entrar, entonces espera a que no haya coches del norte dentro del tunel 
    El semaforo de los coches del norte está bloqueda hasta que no haya coches dentro del tunel
    Le sumamos 1 a car_tunnel_SOUTH para decir que entra en el túnel
    """
    def wants_enter_SOUTH(self):
        self.mutex.acquire()
        self.sem_NORTH.wait_for(self.no_cars_NORTH)
        self.car_tunnel_SOUTH.value += 1
        self.mutex.release()
        
    def leaves_tunnel_SOUTH(self):
        self.mutex.acquire()
        self.car_tunnel_SOUTH.value -= 1
        self.sem_SOUTH.notify_all()
        self.mutex.release()
       
        
       
    def wants_enter_NORTH(self):
        self.mutex.acquire()
        self.sem_SOUTH.wait_for(self.no_cars_SOUTH)
        self.car_tunnel_NORTH.value += 1
        self.mutex.release()
   
    def leaves_tunnel_NORTH(self):
        self.mutex.acquire()
        self.car_tunnel_NORTH.value -= 1
        self.sem_NORTH.notify_all()
        self.mutex.release()
   
    
   
    def wants_enter(self, direction):
        if direction == NORTH:
            self.wants_enter_NORTH()
        else:
            self.wants_enter_SOUTH()
       
    def leaves_tunnel(self,direction):
        if direction == NORTH:
            self.leaves_tunnel_NORTH()
        else:
            self.leaves_tunnel_SOUTH()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    if direction==NORTH:
       delay(3)
    else:
       delay(6)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()