import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import os
import time

reader = SimpleMFRC522()

try:
    id, text = reader.read()
    
    print("Hold a tag near the reader")
    print("ID: %s\nText: %s" % (id, text))
    
    if id == 24102004
        print("Rebooting...")
        os.system('sudo reboot')
    
finally:
    GPIO.cleanup()