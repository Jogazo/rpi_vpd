#!/usr/bin/env python3
import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep

MAX_PWM = 50
MIN_PWM = 18

DEFAULT_ACTIVE = 3
PAUSE = 15

motor_pins = {'enable': 25, 'pin01': 24, 'pin02': 23}


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_pins['enable'], GPIO.OUT)
    GPIO.setup(motor_pins['pin01'], GPIO.OUT)
    GPIO.setup(motor_pins['pin02'], GPIO.OUT)

    return GPIO.PWM(motor_pins['enable'], 100)


def loop(enginepwm):
    enginepwm.start(0)
    while True:
        for x in range(MAX_PWM, MIN_PWM, -1):
            print(x, 'Forward')
            enginepwm.ChangeDutyCycle(x)
            GPIO.output(motor_pins['pin01'], GPIO.HIGH)
            GPIO.output(motor_pins['pin02'], GPIO.LOW)
            sleep(.2)

        print(datetime.now())
        sleep(2)


def destroy():
    GPIO.output(motor_pins['enable'], GPIO.LOW)  # motor stop
    GPIO.cleanup()


if __name__ == '__main__':
    pwm_engine = setup()
    try:
        loop(pwm_engine)
    except KeyboardInterrupt:
        destroy()
