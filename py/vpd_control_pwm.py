#!/usr/bin/env python3
import sys
import select
import tty
import termios
import RPi.GPIO as GPIO


THR_STEP = 5
TURN_STEP = 10

old_settings = termios.tcgetattr(sys.stdin)

throttle_pins = {'enable': 25, 'pin01': 24, 'pin02': 23}
steering_pins = {'enable': 17, 'pin01': 27, 'pin02': 22}


def setup(current_pins):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(current_pins['enable'], GPIO.OUT)
    GPIO.setup(current_pins['pin01'], GPIO.OUT)
    GPIO.setup(current_pins['pin02'], GPIO.OUT)

    return GPIO.PWM(current_pins['enable'], 100)


def update_steering(steer_cycle):
    steer_cycle = min(steer_cycle, 50)
    steer_cycle = max(steer_cycle, -50)
    if steer_cycle >= 0:
        print('R', steer_cycle)
        GPIO.output(steering_pins['pin01'], GPIO.HIGH)
        GPIO.output(steering_pins['pin02'], GPIO.LOW)
    else:
        print('L', steer_cycle)
        GPIO.output(steering_pins['pin01'], GPIO.LOW)
        GPIO.output(steering_pins['pin02'], GPIO.HIGH)

    return steer_cycle


def update(duty_cycle):
    duty_cycle = min(duty_cycle, 100)
    duty_cycle = max(duty_cycle, -100)
    if duty_cycle >= 0:
        print('Forward', duty_cycle)
        GPIO.output(throttle_pins['pin01'], GPIO.HIGH)
        GPIO.output(throttle_pins['pin02'], GPIO.LOW)
    else:
        print('Reverse', duty_cycle)
        GPIO.output(throttle_pins['pin01'], GPIO.LOW)
        GPIO.output(throttle_pins['pin02'], GPIO.HIGH)

    return duty_cycle


def loop(throttle_control, steering_control):
    throttle_control.start(0)
    steering_control.start(0)
    throttle = 0
    turn_deg = 0
    throttle_control.ChangeDutyCycle(throttle)
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
            elif c == 'w':
                throttle += THR_STEP
            elif c == 's':
                throttle -= THR_STEP
            elif c == ' ':
                throttle = 0
                turn_deg = 0  # TODO: substract current value
                print('Stop')
            else:
                print(c)

            throttle_control.ChangeDutyCycle(abs(update(throttle)))
            steering_control.ChangeDutyCycle(abs(update_steering(turn_deg)))


def destroy():
    GPIO.output(throttle_pins['enable'], GPIO.LOW)  # motor stop
    GPIO.output(steering_pins['enable'], GPIO.LOW)  # motor stop
    GPIO.cleanup()
    print('Cleaned up GPIO')


def has_input():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


if __name__ == '__main__':
    throttle_engine = setup(throttle_pins)
    steering_engine = setup(steering_pins)

    try:
        tty.setcbreak(sys.stdin.fileno())
        loop(throttle_engine, steering_engine)
    finally:
        destroy()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
