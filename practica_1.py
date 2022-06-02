"""Práctica1_Esteban_Joaquín_Jiménez_Párraga"""

"""Este problema es un ejemplo del modelo productor-consuidor:
 Toma NPROD procesos que generan números aleatorios en el intervalo [1,9]
 y los almacena en un array común. EL productor toma el mínimo de estos números y los consume 
 añadiendolos a una lista de forma que, si ha ido tomando los mínimos, termina quedando una lista ordenada.
 
 """


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from random import randint
N=10 #cuanto produce cada productor
NPROD = 7 #cuantos productores tenemos




def producer(storage,empty,non_empty,mutex): #Función productor
    pid = int(current_process().name.split('_')[1])
    for i in range(N):
        print(f'productor {pid} produciendo')
        data = randint(1,9)
        empty.acquire()
        add_data(storage,data,pid,mutex)
        non_empty.release()
        print(f'productor {pid} terminó de producir')
    empty.acquire()
    mutex.acquire()
    try:
        storage[pid] = -1 
    finally:
        mutex.release()
    non_empty.release()
    
def add_data(storage, data,pid,mutex): #Añade los datos al storage
    mutex.acquire()
    try:
        storage[pid] = storage[pid] + data
    finally:
        mutex.release()

def consumer(storage,empty,non_empty,mutex,lista_final): #Función consumidor
    for not_emp in non_empty:
        not_emp.acquire()
    acabar = [True] * NPROD 
    while True in acabar:
        data, pos = get_data(storage,mutex,acabar)
        if data != -1:
            lista_final.append(data)
            print(f"consumiendo {data}")
            empty[pos].release()
            non_empty[pos].acquire()
        else:
            acabar = [False]
    print(lista_final)

def get_data(storage,mutex,acabar): #Obtiene el minimo del storage para darselo al consumidor
    mutex.acquire()
    try:
        pos_min, min = -1, -1
        pos_val = []
        for i in range(NPROD):
            if acabar[i]:
                if storage[i] == -1:
                    acabar[i] = False
                else:
                    pos_val.append(i)
        if len(pos_val) == 0:
            acabar = [False]
        else:
            pos_min,min = minimo_selecto(storage, pos_val) 
    finally:
        mutex.release()
    return min, pos_min

def minimo_selecto(storage,pos_val): #Función auxiliar para no tener problemas y tomar el (-1) cuando un productor termina de producir
    if len(pos_val) == 1:
        pos_min = pos_val[0]
        min = storage[pos_min]
    else:
        pos_min = pos_val[0]
        min = storage[pos_min]
        for i in range(1,len(pos_val)):
            j = pos_val[i]
            if min > storage[j]:
                pos_min = j
                min = storage[j]
    return pos_min,min
def main():
    storage = Array('i',NPROD)
    for i in range(NPROD):
        storage[i] = 0
    lista_final=[]
    non_empty = []
    empty = []
    for i in range(NPROD):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(1))

    mutex = Lock()

    prodlist = [ Process(target=producer,
                         name=f'prod_{i}',
                         args=(storage, empty[i], non_empty[i], mutex))
                 for i in range(NPROD) ]
    
    conslist = [ Process(target=consumer,
                         name='cons',
                         args=(storage, empty, non_empty, mutex, lista_final))]
    
    for p in prodlist + conslist:
        p.start()
    
    for p in prodlist + conslist:
        p.join()



if __name__ == '__main__':
    main()