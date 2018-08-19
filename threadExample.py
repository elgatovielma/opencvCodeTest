import threading
import time
import random


def loop1_10():
    x = random.random() * 10
    print("Activa")
    time.sleep(x)
    print("thread 1: " + str(x))


def loop1_11():
    x = random.random() * 10
    time.sleep(x)
    print("thread 2: " + str(x))


def loop1_12():
    x = random.random() * 10
    time.sleep(x)
    print("thread 3: " + str(x))


def loop1_13(y):
    x = random.random() * 10
    time.sleep(x)
    print("thread 4: " + str(x))
    print(y)


t = threading.Thread(target=loop1_10)
threading.Thread(target=loop1_11).start()
threading.Thread(target=loop1_12).start()
threading.Thread(target=loop1_13(2)).start()

t.start()

time.sleep(15)
if not t.is_alive():
    print("No estoy viva!")
else:
    print("Estoy viva")
