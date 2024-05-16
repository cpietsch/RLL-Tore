import gradio as gr
import json
import os

DATA_FILE = 'survey_data.json'

# Sample data structure if the file doesn't exist
sample_data = {
    "active": 2,
    "questions": [
        {"id": 1, "question": "Do you like it?", "yes": 12, "no": 4},
        {"id": 2, "question": "Is the sky blue?", "yes": 1, "no": 6}
    ]
}


data = sample_data

with gr.Blocks() as demo:

    gr.Markdown("### Active Question")
    with gr.Group():
        active_dropdown = gr.Dropdown(label="Select the active question", choices=[
            (item['question'], item['id']) for item in data["questions"]], value=data["active"], interactive=True)

    gr.Markdown("### Questions")

    for index, item in enumerate(data["questions"]):
        with gr.Group():
            with gr.Column():
                with gr.Row():
                    gr.Textbox(value=item['question'],
                               interactive=True, label='question', scale=3, lines=3)

                    with gr.Row():
                        gr.Number(value=item['yes'],
                                  interactive=True, label='yes')
                        gr.Number(value=item['no'],
                                  interactive=True, label='no')
                    gr.Label(
                        value=lambda: f"{item['yes'] + item['no']}", label='total')
                    delete_button = gr.Button(value='Delete')

    gr.Markdown("### New Question")

    with gr.Group():
        gr.Textbox(label="question")
        add_button = gr.Button(value='Add')


if __name__ == "__main__":
    demo.launch()
