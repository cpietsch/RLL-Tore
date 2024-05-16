#!/usr/bin/env python3

import time

import automationhat

if automationhat.is_automation_hat():
    automationhat.light.power.write(1)

while True:
    print("ADC:  {:6.3f}".format(automationhat.analog.read()))
    print("Input 1: {}".format(automationhat.input.one.read()))
    print("Input 2: {}".format(automationhat.input.two.read()))
    print("Input 3: {}".format(automationhat.input.three.read()))

    time.sleep(0.1)
