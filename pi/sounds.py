from time import sleep

import RPi.GPIO as GPIO

BUZZER_PIN = 14
FREQUENCY = 2000
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
pwm = GPIO.PWM(BUZZER_PIN, FREQUENCY)

def beep(duration=0.1):
    pwm.start(80)
    sleep(duration)
    pwm.stop()

def pling():
    try:
        pwm.start(50)

        for freq in [1000, 1200, 1400, 1600]:
            pwm.ChangeFrequency(freq)
            sleep(0.05)

        pwm.stop()
    finally:
        GPIO.output(BUZZER_PIN, GPIO.LOW)

def wrong():
    try:
        pwm.start(70)
        for freq, dur in [(900, 0.06), (700, 0.06), (500, 0.08), (350, 0.10)]:
            pwm.ChangeFrequency(freq)
            sleep(dur)

        pwm.ChangeFrequency(180)
        sleep(0.15)
        pwm.stop()
    finally:
        GPIO.output(BUZZER_PIN, GPIO.LOW)

'''
def beeemp():
    try:
        pwm.start(50)

        for freq in [400, 300, 200, 100]:
            pwm.ChangeFrequency(freq)
            sleep(0.1)

        pwm.stop()
    finally:
        GPIO.output(BUZZER_PIN, GPIO.LOW)'''