#!/usr/bin/env python3

import time
import automationhat

if automationhat.is_automation_hat():
    automationhat.light.power.write(1)

DEBOUNCE = 1

tor1_state = { "time": 0, "state": 0, "count": 0 }
tor2_state = { "time": 0, "state": 0, "count": 0 }

while True:
    tor1 = automationhat.input.one.read()
    tor2 = automationhat.input.two.read()

    if tor1 and tor1_state["state"] == 0 and time.time() - tor1_state["time"] > DEBOUNCE:
        tor1_state["count"] += 1
        print("TOR1: {}".format(tor1_state["count"]))

    if tor1 != tor1_state["state"]:
        tor1_state["time"] = time.time()
        tor1_state["state"] = tor1

    if tor2 and tor2_state["state"] == 0 and time.time() - tor2_state["time"] > DEBOUNCE:
        tor2_state["count"] += 1
        print("TOR2: {}".format(tor2_state["count"]))

    if tor2 != tor2_state["state"]:
        tor2_state["time"] = time.time()
        tor2_state["state"] = tor2
    

    time.sleep(0.02)
