""" Works out if the stereo should be told to dim or not.

Inputs
- Light sensor (Analogue)
- Headlight power (12v?)
- Override force-dim ()
- Override force-bright ()

Outputs
- Dimmer on (12v pos out?)
"""


print("Starting Imports")
#from statistics import mean
from time import sleep
import sys

import machine

TICK_DELAY = 1 # update every x seconds

LIGHT_VAL = 500 # if it's under this, dim the screen.

BRIGHT = 0
DIM = 1

if BRIGHT == DIM:
    raise ValueError("BRIGHT and DIM Can't be the same")


print("Before dim")

def mean(inputdata:list):
    """ calculates the mean of a list of numbers """

    if not isinstance(inputdata, (list, tuple,)):
        if isinstance(inputdata, (float, int)):
            return inputdata
        raise ValueError("Input data is type {}, needs to be list/tuple/float/int".format(type(inputdata)))

    meanval = 0.0

    listlen = len(inputdata)
    for element in inputdata:
        meanval = meanval + float(element)
    result = meanval  / listlen
    return result

class DashLight():
    def __init__(self):
        print("In init")
        self.light_max = 0 # 560 in the breadboard with the iphone light on it
        self.light_min = 65535 # 2000ish in the breadboard in the kitchen

        self.light = -1
        self.light_history = []
        self.light_average = -1

        self.headlight = False

        self.override_dim = False

        self.output = False
        self.pins = {
            "in_light" : 26,            # GP26 / ADC0
            "in_headlight" : 0,         # GP0
            "in_override_bright" : 2,   # GP2
            "in_override_dim" : 3,      # GP3
            "out_dim" : 10,             # GP10
        }

        self.io = {
            "in_light" : machine.ADC(self.pins["in_light"]),
            "in_headlight" : machine.Pin(self.pins["in_headlight"],
                           machine.Pin.IN,
                           machine.Pin.PULL_UP,
                          ),
            "in_override_bright" : machine.Pin(self.pins["in_override_bright"],
                           machine.Pin.IN,
                           machine.Pin.PULL_UP,
                          ),
            "in_override_dim" : machine.Pin(self.pins["in_override_dim"],
                           machine.Pin.IN,
                           machine.Pin.PULL_UP,
                          ),
            "out_dim" : machine.Pin(self.pins["out_dim"], machine.Pin.OUT),
        }

        # maybe set an interrupt on the overrides?
        # p2.irq(lambda pin: print("IRQ with flags:", pin.irq().flags()), Pin.IRQ_FALLING)

    def _input_pin_pullup(self, pin: str):
        """ returns a configured input pin with pullup"""
        return machine.Pin(self.pins[pin],
                           machine.Pin.IN,
                           machine.Pin.PULL_UP,
                          )

    def read_sensors(self):
        """ reads the sensors """

        # read light sensor
        self.light = self.io["in_light"].read_u16()
        if self.light < self.light_min:
            self.light_min = self.light
        if self.light > self.light_max:
            self.light_max = self.light

        print("Light: {} ({} - {})".format(
            self.light,
            self.light_min,
            self.light_max,
            )
        )


        self.override = 0


        override_dim = self.io["in_override_dim"].value()
        override_bright = self.io["in_override_bright"].value()
        print("Dim: {}".format(override_dim))
        print("Bri: {}".format(override_bright))
        # read headlight input
        #self.light = self.io["in_headlight"].value()
        #print(dir(self.io["in_headlight"]))
        # read override_dim
        # read override_light
        # TODO: when override_dim and override_bright are both true, wtf?

        pass

    def loop(self):
        """ main loop """
        while 1==1:
            self.tick()
            print("Tick")
            sleep(TICK_DELAY)


    def tick(self):
        """ does a full cycle of things """
        self.read_sensors()
        self.update_light_average()
        self.update_output()

    def update_light_average(self):
        """updates the rolling average of light readings"""

        # keep a minimum of five history values
        if len(self.light_history) > 5:
            self.light_history.pop(0)

        # only if it's updated from start
        if self.light >= 0:
            self.light_history.append(self.light)

        self.light_average = mean(self.light_history)

    def update_output(self):
        """sets the output"""
        # make it dim
        if self.override == -1:
            self.output = DIM
        # make it bright
        elif self.override == 1:
            self.output = BRIGHT
        else:
            if self.light_average > LIGHT_VAL:
                self.output = BRIGHT
            else:
                self.output = DIM

        # set the pin
        # self.pins["out_dim"](self.output)



dashlight = DashLight()
dashlight.loop()

