########################################################
############ COPYRIGHT (c) 2019 Tesla Works ############
########################################################
##################### engine.py ########################
########################################################

import os
from include.listener import Listener

def engine():
    print("Running engine.py")

    myListener = Listener()
    myListener.printName()


if __name__ == "__main__":
    engine()