# -*- coding: utf-8 -*-
from gpiozero import Button
from funktionen import *


#Pin der das Spiel startet
start_button = Button(12)

while True:
    if start_button.is_pressed:
        Draht()
        time.sleep(1)