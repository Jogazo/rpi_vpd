#!/usr/bin/env python3
import sys
import select
import tty
import termios
import RPi.GPIO as GPIO


TURN_STEP = 10

old_settings = termios.tcgetattr(sys.stdin)

motor_pins = {'enable': 25, 'pin01': 24, 'pin02': 23}
steer_pins = {'enable': 17, 'pin01': 27, 'pin02': 22}


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(steer_pins['enable'], GPIO.OUT)
    GPIO.setup(steer_pins['pin01'], GPIO.OUT)
    GPIO.setup(steer_pins['pin02'], GPIO.OUT)

    return GPIO.PWM(steer_pins['enable'], 100)


def update_steering(duty_cycle):
    duty_cycle = min(duty_cycle, 50)
    duty_cycle = max(duty_cycle, -50)
    if duty_cycle >= 0:
        print('R', duty_cycle)
        GPIO.output(steer_pins['pin01'], GPIO.HIGH)
        GPIO.output(steer_pins['pin02'], GPIO.LOW)
    else:
        print('L', duty_cycle)
        GPIO.output(steer_pins['pin01'], GPIO.LOW)
        GPIO.output(steer_pins['pin02'], GPIO.HIGH)

    return duty_cycle


def loop(steering_control):
    steering_control.start(0)
    turn_deg = 0
    steering_control.ChangeDutyCycle(turn_deg)

    while True:
        if has_input():
            c = sys.stdin.read(1)

            if c == '\x1b':
                print('Exit.')
                break
            elif c == 'a':
                turn_deg += TURN_STEP
            elif c == 'd':
                turn_deg -= TURN_STEP
            elif c == ' ':
                turn_deg = 0
                print('Stop')
            else:
                print(c)

            steering_control.ChangeDutyCycle(abs(update_steering(turn_deg)))


def destroy():
    GPIO.output(steer_pins['enable'], GPIO.LOW)  # motor stop
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
