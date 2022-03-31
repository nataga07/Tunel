# -*- coding: utf-8 -*-

"""
Autoras: Claudia Casado Poyatos, Natalia García Domínguez y Olga Rodríguez Acevedo
"""

"""
Este programa controla el flujo de coches que atraviesan un tunel con el objetivo de que 
no haya accidentes, ya que éste únicamente permite el paso de vehículos en una dirección.
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
        self.car_NORTH = Value('i',0) # Número de coches dentro del tunel que vienen del norte y van hacia el sur.
        self.car_SOUTH = Value('i',0) # Número de coches dentro del tunel que vienen del sur y van hacia el norte.
        self.mutex = Lock()
        self.no_inside_NORTH = Condition(self.mutex) # Variable condición que asegura el cumplimiento del invariante y que 
                                                     # se hará cierta si no hay coches que vienen del norte dentro del tunel.
        self.no_inside_SOUTH = Condition(self.mutex) # Variable condición que asegura el cumplimiento del invariante y que 
                                                     # se hará cierta si no hay coches que vienen del sur dentro del tunel.

    # Función que indica si no hay coches que vienen del norte dentro del tunel.
    def no_cars_NORTH(self): 
        return self.car_NORTH.value == 0
   
    # Función que indica si no hay coches que vienen del sur dentro del tunel.
    def no_cars_SOUTH(self): 
        return self.car_SOUTH.value == 0

    # Función que se ejecuta cuando un coche que viene del sur quiere entrar en el tunel. 
    # Ésta, además, permite que dicho coche lo atraviese, habiéndose asegurado antes de 
    # que en el tunel no hay coches que vienen del norte. 
    def wants_enter_SOUTH(self): 
        self.mutex.acquire()    
        self.no_inside_NORTH.wait_for(self.no_cars_NORTH)
        self.car_SOUTH.value += 1
        self.mutex.release()
        
    # Función que se ejecuta cuando un coche que viene del sur está saliendo del tunel.   
    def leaves_tunnel_SOUTH(self): 
        self.mutex.acquire()
        self.car_SOUTH.value -= 1
        self.no_inside_SOUTH.notify_all()
        self.mutex.release()
      
    # Función que se ejecuta cuando un coche que viene del norte quiere entrar en el tunel. 
    # Ésta, además, permite que dicho coche lo atraviese, habiéndose asegurado antes de 
    # que en el tunel no hay coches que vienen del sur. 
    def wants_enter_NORTH(self):
        self.mutex.acquire()
        self.no_inside_SOUTH.wait_for(self.no_cars_SOUTH)
        self.car_NORTH.value += 1
        self.mutex.release()

    # Función que se ejecuta cuando un coche que viene del norte está saliendo del tunel.  
    def leaves_tunnel_NORTH(self):
        self.mutex.acquire()
        self.car_NORTH.value -= 1
        self.no_inside_NORTH.notify_all()
        self.mutex.release()
   
    #funcion general para entrar depdendiendo de la direccion 
    def wants_enter(self, direction):
        if direction == NORTH:
            self.wants_enter_NORTH()
        else:
            self.wants_enter_SOUTH()

    #funcion general para salir dependediendo de la direccion       
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
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")

def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0, 1) == 1 else SOUTH
        cid += 1
        p = Process(target = car, args = (cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1 / 0.5)) # Un nuevo coche entra cada 0.5 segundos.

if __name__ == '__main__':
    main()
