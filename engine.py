########################################################
############ COPYRIGHT (c) 2019 Tesla Works ############
########################################################
##################### engine.py ########################
########################################################

import os
#from include.listener import Listener
from include.loader import Loader
import time

def engine():
    print("Running engine.py")

    myLoader = Loader()

    myLoader.setServoAngle(18,10)
    time.sleep(5)
    myLoader.setServoAngle(13,29)
    time.sleep(5)
    myLoader.setServoAngle(18, 30)
    myLoader.setServoAngle(13, 10)

    print("Finished running engine.py")

    #mqttc = Listener()
    #rc = mqttc.run()

    #print("rc: " + str(rc))


if __name__ == "__main__":
    engine()
