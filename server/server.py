import gradio as gr
import json
import os

DATA_FILE = 'survey_data.json'

# Sample data structure if the file doesn't exist
default_data = [
    {"active": False, "question": "Do you like it?", "yes": 12, "no": 4},
    {"active": True, "question": "Is the sky blue?", "yes": 1, "no": 6}
]


# def create_interface():
#     data = default_data
#     interface = []

#     for index, item in enumerate(data):
#         with gr.Row():
#             gr.Textbox(value=item['question'],
#                        interactive=False, label='question')
#             gr.Textbox(value=item['yes'], interactive=False, label='yes')
#             gr.Textbox(value=item['no'], interactive=False, label='no')

#             delete_button = gr.Button(value='Delete')
#     # add separator space
#     gr.Textbox(value='', interactive=False, label='')

#     # Add a new question
#     with gr.Row():
#         new_question_textbox = gr.Textbox(label='New Question')
#         add_button = gr.Button(value='Add')

#     return interface


# with gr.Blocks() as demo:
#     gr.Markdown("### Survey Interface")
#     interface = create_interface()


if __name__ == "__main__":
    demo.launch()
