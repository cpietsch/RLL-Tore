import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import List, Dict
from pydantic import BaseModel
import uvicorn
import asyncio
import automationhat


app = FastAPI()

DATA_FILE = "data.json"
DEBOUNCE = 1

class Question(BaseModel):
    id: int
    question: str
    yes: int = 0
    no: int = 0


class Data(BaseModel):
    active: int = 0
    last_id: int = 0
    questions: List[Question] = []


class VoteState(BaseModel):
    state: int = 0
    count: int = 0
    time: float = 0
    last: float = 0


class Connections():
    connections: List[WebSocket] = []

    def add_connection(self, websocket: WebSocket):
        self.connections.append(websocket)

    def remove_connection(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, data: Dict):
        for connection in self.connections:
            await connection.send_json(data)


def load_data() -> Data:
    try:
        with open(DATA_FILE, "r") as f:
            return Data(**json.load(f))
    except FileNotFoundError:
        return Data()


def save_data(data: Data):
    with open(DATA_FILE, "w") as f:
        json.dump(data.model_dump(), f, indent=2)


def get_yes_no(data: Data) -> Dict:
    yes = 0
    no = 0
    for q in data.questions:
        if q.id == data.active:
            yes = q.yes
            no = q.no
            break
    return {"yes": yes, "no": no}

async def add_vote_active(yes = 0, no = 0):
    for q in data.questions:
        if q.id == data.active:
            q.yes += yes
            q.no += no
            print("YES: {}, NO: {}, {}".format(q.yes, q.no, q.question))
            break
    # broadcast updated data
    await connections.broadcast(data.model_dump())
    save_data(data)

data = load_data()
connections = Connections()

tor1_state = VoteState(count=get_yes_no(data)["yes"])
tor2_state = VoteState(count=get_yes_no(data)["no"])

async def input_counter_loop():
    # global tor1_state, tor2_state
    while True:
        tor1 = automationhat.input.one.read()
        tor2 = automationhat.input.two.read()

        if tor1 and tor1_state.state == 0 and time.time() - tor1_state.time > DEBOUNCE:
            tor1_state.count += 1
            tor1_state.last = time.time()
            # print("TOR1: {}".format(tor1_state.count))
            automationhat.light.warn.on()
            await add_vote_active(yes=1)

        if tor1_state.last and time.time() - tor1_state.last > 0.5:
            automationhat.light.warn.off()
            tor1_state.last = 0

        if tor1 != tor1_state.state:
            tor1_state.time = time.time()
            tor1_state.state = tor1

        if tor2 and tor2_state.state == 0 and time.time() - tor2_state.time > DEBOUNCE:
            tor2_state.count += 1
            tor2_state.last = time.time()
            # print("TOR2: {}".format(tor2_state.count))
            automationhat.light.comms.on()
            await add_vote_active(no=1)

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # global tor1_state, tor2_state
    await websocket.accept()
    connections.add_connection(websocket)

    try:
        await websocket.send_json(data.model_dump())

        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            if action == "update_votes":
                question_id = message["id"]
                yes = message["yes"]
                no = message["no"]
                for q in data.questions:
                    if q.id == question_id:
                        q.yes = yes
                        q.no = no
                        break
            elif action == "add_question":
                data.last_id += 1
                new_question = Question(
                    id=data.last_id, question=message["question"])

                data.questions.append(new_question)
            elif action == "delete_question":
                question_id = message["id"]
                data.questions = [
                    q for q in data.questions if q.id != question_id]
            elif action == "set_active":
                data.active = message["id"]
                # tor1_state = VoteState(count=get_yes_no(data)["yes"])
                # tor2_state = VoteState(count=get_yes_no(data)["no"])

            save_data(data)
            # Broadcast updated data
            # await websocket.send_json(data.model_dump_json())
            await connections.broadcast(data.model_dump())

    except WebSocketDisconnect:
        connections.remove_connection(websocket)
        pass


html_admin = """
<!DOCTYPE html>
<html>
    <head>
        <title>Tor Admin</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            h1 {
                color: #333;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 10px 0;
            }
            form {
                margin-top: 20px;
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 1em;
            }
            input[type="text"] {
                padding: 5px;
                font-size: 16px;
            }
            button {
                padding: 5px 10px;
                font-size: 16px;
                background-color: #333;
                color: white;
                border: none;
                cursor: pointer;
            }
            select {
                padding: 5px;
                font-size: 16px;
            }
            container {
                display: flex;
                flex-direction: column;
                max-width: 800px;
                margin: 0 auto;
            }

            question {
                display: grid;
                grid-template-columns: 4fr 1fr 1fr;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }
            question.active {
                border: 1px solid #333;
            }
            question span {
                justify-self: center;
            }
            question span:first-child {
                justify-self: start;
            }

        </style>
    </head>
    <body>
    <container>
        <h1>Tor Admin</h1>
        <div id="questions"></div>
        
        <form id="active_form">
            <select id="active">
            </select>
            <button type="submit">Set Active</button>
        </form>

        <form id="delete_form">
            <select id="delete">
            </select>
            <button type="submit">Delete Question</button>
        </form>

        <form id="form">
            <input type="text" id="question" placeholder="Enter your question" required>
            <button type="submit">Add Question</button>
        </form>

    </container>

        <script>
            let ws = new WebSocket("ws://tor.local:8000/ws");
            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);
                let active = data.active;
                console.log(data);
                let questions = document.getElementById("questions");
                questions.innerHTML = "";
                data.questions.forEach(question => {
                    let div = document.createElement("question");
                    div.className = question.id === active ? "active" : "";
                    let q = document.createElement("span");
                    q.textContent = question.question;
                    let yes = document.createElement("span");
                    yes.textContent = `Yes: ${question.yes}`;
                    let no = document.createElement("span");
                    no.textContent = `No: ${question.no}`;
                    div.appendChild(q);
                    div.appendChild(yes);
                    div.appendChild(no);

                    questions.appendChild(div);
                });

                // add options to select
                let select = document.getElementById("active")
                select.innerHTML = "";
                let delete_select = document.getElementById("delete")
                delete_select.innerHTML = "";
                data.questions.forEach(question => {
                    let option = document.createElement("option");
                    option.textContent = question.question;
                    option.value = question.id;
                    if (question.id === active) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                    delete_select.appendChild(option.cloneNode(true));
                });
            };
            
            document.getElementById("form").onsubmit = function(event) {
                event.preventDefault();
                let question = document.getElementById("question").value;
                ws.send(JSON.stringify({action: "add_question", question: question}));
                document.getElementById("question").value = "";
            };

            document.getElementById("active_form").onsubmit = function(event) {
                event.preventDefault();
                let active = document.getElementById("active").value;
                ws.send(JSON.stringify({action: "set_active", id: parseInt(active)}));
            };

            document.getElementById("delete_form").onsubmit = function(event) {
                event.preventDefault();
                let delete_question = document.getElementById("delete").value;
                ws.send(JSON.stringify({action: "delete_question", id: parseInt(delete_question)}));
            };

        </script>
       
    </body>
</html>
"""

html_screen = """
<!DOCTYPE html>
<html>
    <head>
        <title>Tor Screen</title>
        <style>
            body {
                font-family: sans-serif;
                padding: 0;
                margin: 0;
            }
            
            #question {
                display: flex;
                flex-direction: column;
                width: 100vw;
                height: 100vh;
                justify-content: center;
                align-items: center;
                font-size: 4em;
                background-color: #000;
                color: #fff;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div id="question"></div>

        <script>
            let ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);
                let active = data.active;
                
                let questions = document.getElementById("question");
                let active_question = data.questions.find(q => q.id === active);
                questions.innerHTML = active_question.question;
            };

        </script>
       
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html_admin)


@app.get("/screen")
async def get():
    return HTMLResponse(html_screen)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
