########################################################
############ COPYRIGHT (c) 2019 Tesla Works ############
########################################################
#################### loader.py #######################
########################################################

import os
import RPi.GPIO as GPIO
from time import sleep
def setServoAngle(pin, deg):
	if deg>60:
		return False
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	pwm=GPIO.PWM(pin, 50)
	pwm.start(0)
	duty= deg/18 + 2
	GPIO.output(pin, True)
	pwm.ChangeDutyCycle(duty)
	sleep(1)
	GPIO.output(pin, False)
	pwm.ChangeDutyCycle(0)
	pwm.stop()
	GPIO.cleanup()
	return True

class Loader:

  def __init__(self):
    self.name = "loader"