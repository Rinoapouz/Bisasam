# -*- coding: utf-8 -*-
from gpiozero import Button, LED, LEDCharDisplay, LEDMultiCharDisplay
from threading import Thread, Event
from time import sleep
import time
import datetime
import mysql.connector
from config import strafsekunden, maxfehler, maxzeit

# LEDs, Draht und keule
Abschluss = Button(0)
Fehler = Button(21)
redLED = LED(20)
greenLED = LED(16)

# 7-segment display Pins
comU = LED(13)
comO = LED(8)
DP = LED(24)
a = LED(19)
b = LED(26)
c = LED(25)
d = LED(7)
e = LED(1)
f = LED(6)
g = LED(5)

# 4x 7 Segment
cc = LEDCharDisplay(27, 22, 10, 9, 11, 15, 18, active_high=False)
zeitanzeige = LEDMultiCharDisplay(cc, 17, 14, 3, 2)

# Start button
start_button = Button(12)

############################################################################################
mydb = mysql.connector.connect(
    host="localhost",
    user="Daniel",
    password="Daniel",
    database="DRAHT"
)
mycursor = mydb.cursor()

# 7 Segment display function
def segment(val):
    if val == 1:
        a.off(), b.on(), c.on(), d.off(), e.off(), f.off(), g.off()
    elif val == 2:
        a.on(), b.on(), c.off(), d.on(), e.on(), f.off(), g.on()
    elif val == 3:
        a.on(), b.on(), c.on(), d.on(), e.off(), f.off(), g.on()
    elif val == 4:
        a.off(), b.on(), c.on(), d.off(), e.off(), f.on(), g.on()
    elif val == 5:
        a.on(), b.off(), c.on(), d.on(), e.off(), f.on(), g.on()
    elif val == 6:
        a.on(), b.off(), c.on(), d.on(), e.on(), f.on(), g.on()
    elif val == 7:
        a.on(), b.on(), c.on(), d.off(), e.off(), f.off(), g.off()
    elif val == 8:
        a.on(), b.on(), c.on(), d.on(), e.on(), f.on(), g.on()
    elif val == 9:
        a.on(), b.on(), c.on(), d.on(), e.off(), f.on(), g.on()
    elif val == 0:
        a.on(), b.on(), c.on(), d.on(), e.on(), f.on(), g.off()

def clean():
    zeitanzeige.value = ""
    segment(0)
    redLED.off()
    greenLED.off()

# Zeit und Fehler auf 0 setzen
stop_event = Event()
state = {"zeit": 0, "fehler": 0}

# Zeit Messung und Anzeige auf das 4x 7 Segment
def zeit_messung():
    while not stop_event.is_set():
        zeitanzeige.value = str(state["zeit"])
        state["zeit"] += 1
        time.sleep(1)
        if state["zeit"] >= maxzeit:
            stop_event.set()

# Checkt auf eine Berührung, wenn eine da ist state[fehler] += 1 und LED tauschen
def Fehler_tracker():
    while not stop_event.is_set():
        if Fehler.is_pressed:
            state["fehler"] += 1
            segment(state["fehler"])
            redLED.on()
            greenLED.off()
        else:
            redLED.off()
            greenLED.on()
        if state["fehler"] >= maxfehler:
            stop_event.set()
        time.sleep(0.25)

def Abschluss_tracker():
    while not stop_event.is_set():
        if Abschluss.is_pressed:
            stop_event.set()
        time.sleep(0.1)

def Draht():
    global stop_event, state

    # Reset shared state and stop_event
    stop_event = Event()
    state = {"zeit": 0, "fehler": 0}

    # Start the threads
    threads = [
        Thread(target=zeit_messung),
        Thread(target=Fehler_tracker),
        Thread(target=Abschluss_tracker),
    ]

    for thread in threads:
        thread.start()

    # Wait for any thread to signal stop
    stop_event.wait()

    # Calculate final time and insert into database
    officialtime = strafsekunden * state["fehler"] + state["zeit"]
    sql = "INSERT INTO Zeiten (mistake, time) VALUES (%s, %s)"
    val = (state["fehler"], officialtime)
    mycursor.execute(sql, val)
    mydb.commit()

    # Ensure all threads are properly terminated
    for thread in threads:
        thread.join()

# Main loop to wait for the start button press
while True:
    if start_button.is_pressed:
        clean()
        Draht()
        # Optional: Add a delay to debounce the start button
        time.sleep(1)
