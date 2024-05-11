#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

DELAY = 0.5
ITERATIONS = 10
LED_PIN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(LED_PIN, GPIO.OUT)

for i in range(ITERATIONS):
    print('LED ON')
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(DELAY)
    print('LED OFF')
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(DELAY)

print('done!')
