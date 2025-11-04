# main.py for the micro:bit
from microbit import *
import time

uart.init(baudrate=115200)

# Discard the initial reading to stabilise
_ = temperature()
time.sleep(5)

while True:
    temp = temperature()
    print(f"temp:{temp}")
    time.sleep(30)
