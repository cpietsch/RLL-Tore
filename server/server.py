import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict
from pydantic import BaseModel
import uvicorn

app = FastAPI()

DATA_FILE = "data.json"


class Question(BaseModel):
    id: int
    question: str
    yes: int = 0
    no: int = 0


class Data(BaseModel):
    active: int = 0
    last_id: int = 0
    questions: List[Question] = []


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


data = load_data()
connections = Connections()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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

            save_data(data)
            # Broadcast updated data
            # await websocket.send_json(data.model_dump_json())
            await connections.broadcast(data.model_dump())

    except WebSocketDisconnect:
        connections.remove_connection(websocket)
        pass


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Example</title>
    </head>
    <body>
        <h1>WebSocket Example</h1>
        <ul id="questions"></ul>
        <script>
            let ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);
                let active = data.active;
                console.log(data);
                let questions = document.getElementById("questions");
                questions.innerHTML = "";
                data.questions.forEach(question => {
                    let li = document.createElement("li");
                    li.textContent = `${question.question} - Yes: ${question.yes}, No: ${question.no}, active: ${active === question.id}`;
                    questions.appendChild(li);
                });
            };
            // Send messages from your frontend here
        </script>
       
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
