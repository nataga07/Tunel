# -*- coding: utf-8 -*-
"""
TUNEL TURNOS 
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
        self.turno = Value('i',0) #0 si pasan los del Norte y 1 si pasan los del SUR
        self.queue_NORTH = Value('i',0)
        self.queue_SOUTH = Value('i',0)
        
    def no_cars_NORTH(self):
        return self.car_tunnel_NORTH.value == 0 and (self.turno.value == 1 or self.queue_NORTH.value == 0)
    
    def no_cars_SOUTH(self): 
        return self.car_tunnel_SOUTH.value == 0 and (self.turno.value == 0 or self.queue_SOUTH.value == 0)
    
    def wants_enter_SOUTH(self):
        self.mutex.acquire()
        self.queue_SOUTH.value += 1
        self.sem_NORTH.wait_for(self.no_cars_NORTH)
        self.queue_SOUTH.value -= 1
        self.car_tunnel_SOUTH.value += 1
        self.mutex.release()
        
    def leaves_tunnel_SOUTH(self):
        self.mutex.acquire()
        self.car_tunnel_SOUTH.value -= 1
        self.turno.value = 0
        self.sem_SOUTH.notify_all()
        self.mutex.release()


    def wants_enter_NORTH(self):
        self.mutex.acquire()
        self.queue_NORTH.value += 1
        self.sem_SOUTH.wait_for(self.no_cars_SOUTH)
        self.queue_NORTH.value -= 1
        self.car_tunnel_NORTH.value += 1
        self.mutex.release()
        
    def leaves_tunnel_NORTH(self):
        self.mutex.acquire()
        self.car_tunnel_NORTH.value -= 1
        self.turno.value = 1
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