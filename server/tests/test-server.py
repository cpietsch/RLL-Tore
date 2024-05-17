#!/usr/bin/env python3

from dataclasses import dataclass
import time
import threading
from fastapi import FastAPI
import uvicorn
import asyncio

import automationhat

DEBOUNCE = 1

@dataclass
class VoteState:
    state: int = 0
    count: int = 0
    time: float = 0
    last: float = 0

tor1_state = VoteState()
tor2_state = VoteState()


app = FastAPI()

@app.get("/votes")
def get_votes():
    return {"tor1": tor1_state.count, "tor2": tor2_state.count}


async def input_counter_loop():
    global tor1_state, tor2_state
    while True:
        tor1 = automationhat.input.one.read()
        tor2 = automationhat.input.two.read()

        if tor1 and tor1_state.state == 0 and time.time() - tor1_state.time > DEBOUNCE:
            tor1_state.count += 1
            tor1_state.last = time.time()
            print("TOR1: {}".format(tor1_state.count))
            automationhat.light.warn.on()

        if tor1_state.last and time.time() - tor1_state.last > 0.5:
            automationhat.light.warn.off()
            tor1_state.last = 0

        if tor1 != tor1_state.state:
            tor1_state.time = time.time()
            tor1_state.state = tor1

        if tor2 and tor2_state.state == 0 and time.time() - tor2_state.time > DEBOUNCE:
            tor2_state.count += 1
            tor2_state.last = time.time()
            print("TOR2: {}".format(tor2_state.count))
            automationhat.light.comms.on()

        if tor2_state.last and time.time() - tor2_state.last > 0.5:
            automationhat.light.comms.off()
            tor2_state.last = 0

        if tor2 != tor2_state.state:
            tor2_state.time = time.time()
            tor2_state.state = tor2

        await asyncio.sleep(0.02)

@app.on_event("startup")
async def start_background_tasks():
    # Start the input counter loop in the background
    asyncio.create_task(input_counter_loop())

if __name__ == "__main__":
    # Alternative: Run FastAPI in production using Gunicorn (recommended)
    uvicorn.run("test-server:app", host="0.0.0.0", port=8000, reload=True)
