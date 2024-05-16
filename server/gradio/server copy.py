import gradio as gr
import json
import os

# Initialize with some questions
questions = [
    {"active": False, "question": "Do you like it?", "yes": 12, "no": 4},
    {"active": True, "question": "Is the sky blue?", "yes": 1, "no": 6}
]

# File to save/load questions
QUESTIONS_FILE = "questions.json"


def load_questions():
    global questions
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as f:
            questions = json.load(f)
    else:
        save_questions()


def save_questions():
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f)


def refresh_questions():
    return gr.update(value=[[q['active'], q['question'], q['yes'], q['no']] for q in questions])


def add_question(question):
    global questions
    questions.append(
        {"active": False, "question": question, "yes": 0, "no": 0})
    save_questions()
    return refresh_questions()


def delete_question(index):
    global questions
    if 0 <= index < len(questions):
        del questions[index]
    save_questions()
    return refresh_questions()


def toggle_active(index):
    global questions
    if 0 <= index < len(questions):
        questions[index]['active'] = not questions[index]['active']
    save_questions()
    return refresh_questions()


def answer_question(index, answer):
    global questions
    if 0 <= index < len(questions):
        if answer == "Yes":
            questions[index]["yes"] += 1
        elif answer == "No":
            questions[index]["no"] += 1
    save_questions()
    return refresh_questions()


load_questions()

with gr.Blocks() as demo:
    gr.Markdown("## Questionnaire")
    question_table = gr.DataFrame(
        headers=["Active", "Question", "Yes", "No"],
        type="array",
        interactive=False,
        value=[[q['active'], q['question'], q['yes'], q['no']]
               for q in questions]
    )

    with gr.Row():
        new_question_box = gr.Textbox(placeholder="New question")
        add_button = gr.Button("Add")

    with gr.Row():
        question_index = gr.Number(label="Question index", precision=0)
        toggle_button = gr.Button("Toggle Active")
        delete_button = gr.Button("Delete")

    with gr.Row():
        answer_index = gr.Number(label="Question index", precision=0)
        answer_choice = gr.Radio(["Yes", "No"], label="Answer")
        answer_button = gr.Button("Submit Answer")

    add_button.click(add_question, inputs=new_question_box,
                     outputs=question_table)
    delete_button.click(
        delete_question, inputs=question_index, outputs=question_table)
    toggle_button.click(toggle_active, inputs=question_index,
                        outputs=question_table)
    answer_button.click(answer_question, inputs=[
                        answer_index, answer_choice], outputs=question_table)

demo.launch()
