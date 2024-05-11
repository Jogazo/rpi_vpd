#!/usr/bin/env python3
import sys
import select
import tty
import termios
import RPi.GPIO as GPIO


THR_STEP = 5

old_settings = termios.tcgetattr(sys.stdin)

motor_pins = {'enable': 25, 'pin01': 24, 'pin02': 23}
steer_pins = {'enable': 17, 'pin01': 27, 'pin02': 22}


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_pins['enable'], GPIO.OUT)
    GPIO.setup(motor_pins['pin01'], GPIO.OUT)
    GPIO.setup(motor_pins['pin02'], GPIO.OUT)

    return GPIO.PWM(motor_pins['enable'], 100)


def update(duty_cycle):
    duty_cycle = min(duty_cycle, 100)
    duty_cycle = max(duty_cycle, -100)
    if duty_cycle >= 0:
        print('Forward', duty_cycle)
        GPIO.output(motor_pins['pin01'], GPIO.HIGH)
        GPIO.output(motor_pins['pin02'], GPIO.LOW)
    else:
        print('Reverse', duty_cycle)
        GPIO.output(motor_pins['pin01'], GPIO.LOW)
        GPIO.output(motor_pins['pin02'], GPIO.HIGH)

    return duty_cycle


def loop(throttle_control):
    throttle_control.start(0)
    throttle = 0
    throttle_control.ChangeDutyCycle(throttle)

    while True:
        if has_input():
            c = sys.stdin.read(1)

            if c == '\x1b':
                print('Exit.')
                break
            elif c == 'w':
                throttle += THR_STEP
            elif c == 's':
                throttle -= THR_STEP
            elif c == ' ':
                throttle = 0
                print('Stop')
            else:
                print(c)

            throttle_control.ChangeDutyCycle(abs(update(throttle)))


def destroy():
    GPIO.output(motor_pins['enable'], GPIO.LOW)  # motor stop
    GPIO.cleanup()
    print('Cleaned up GPIO')


def has_input():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


if __name__ == '__main__':
    pwm_engine = setup()

    try:
        tty.setcbreak(sys.stdin.fileno())
        loop(pwm_engine)
    finally:
        destroy()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
