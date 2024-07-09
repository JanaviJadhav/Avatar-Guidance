import gradio as gr
from PIL import Image
import base64
from io import BytesIO
from backend import get_documents, run_docbot,run_synthvision,post_processing,bot  # Import the backend functions

# Global state to keep track of current image index and chat history
current_image_index = 0
images = []
chat_history = []

# Function to process input and simulate a response
def process_input(doc, img, caption, message):
    global images, chat_history

    if doc:
        response = f"Received document: {doc.name}"
        # Call the backend function to process the document and image
        get_documents(img.name if img else "", caption if img else "", doc.name)
    elif img:
        response = f"Received image: {img.name}"
        # If an image is uploaded, store it in images list
        img_data = Image.open(img)
        images.append((img_data, caption or "No caption provided"))
    else:
        response = f"Processing your message: {message}"
        # Call the backend bot function to get a response
        if chat_history and chat_history[0][0] == doc.name:
            gradio_response = bot(message, doc.name)
            response += f"\nBot Response: {gradio_response}"

    # Add user input and bot response to chat history
    chat_history.append((message, response))

    # Update chatbot display
    return update_chatbot()

# Function to update chatbot display
def update_chatbot():
    global images, current_image_index, chat_history

    chat_history_display = chat_history.copy()  # Make a copy to avoid modifying original

    if images:
        img_data = images[current_image_index][0]
        caption = images[current_image_index][1]

        # Encode image to base64 string
        buffered = BytesIO()
        img_data.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        img_html = f"""
        <div style="text-align:center; position:relative; display:inline-block;">
            <img src="data:image/png;base64,{img_str}" style="max-width:100px; max-height:100px; border-radius:5px;">
            <div style="position:absolute; top:0; left:50%; transform:translateX(-50%); background-color:#8D99AE; color:white; border-radius:5px; padding:2px 5px; font-size:12px;">
                {current_image_index + 1}/{len(images)}
            </div>
            <br><span>{current_image_index + 1}: {caption}</span>
        </div>
        """

        chat_history_display.append((None, img_html))
    
    # Update visibility of navigation buttons
    previous_visible = next_visible = bool(images)

    return chat_history_display, gr.update(visible=previous_visible), gr.update(visible=next_visible)

# Function to get the next image and caption
def next_image():
    global current_image_index, images
    if images:
        current_image_index = (current_image_index + 1) % len(images)
    return update_chatbot()

# Function to get the previous image and caption
def previous_image():
    global current_image_index, images
    if images:
        current_image_index = (current_image_index - 1) % len(images)
    return update_chatbot()

# Function to handle the navigation to the chatbot page
def navigate_to_chatbot(doc, img):
    if not doc and not img:
        return gr.update(visible=True), gr.update(visible=False), gr.update(value="Please upload a PDF document or an image first."), None, None
    else:
        return gr.update(visible=False), gr.update(visible=True), gr.update(value=""), None, None

# Define the Gradio interface
with gr.Blocks(css="""
    .gradio-container {
        background-color: #2B2D42; 
        color: white; 
        font-family: Arial, sans-serif;
        padding: 20px;
    }
    .upload-doc, .upload-img, .message-box {
        background-color: #8D99AE; 
        padding: 10px; 
        border-radius: 5px; 
        text-align: center; 
        margin: 5px;
        font-size: 12px;
        color: white;
    }
    .submit-btn {
        font-family: inherit;
        font-size: 20px;
        background: royalblue;
        color: white;
        padding: 0.7em 1em;
        padding-left: 0.9em;
        display: flex;
        align-items: center;
        border: none;
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.2s;
        cursor: pointer;
    }
    .chatbox {
        background-color: #8D99AE; 
        padding: 10px; 
        border-radius: 5px; 
        margin: 5px;
        min-height: 300px;
    }
    .avatar-guidance-title {
        color: white; 
        font-size: 24px; 
        padding: 10px 0; 
        text-align:center;
    }
    .previous-btn {
        font-size: 20px;
        padding: 10px;
        margin: 10px;
        background-color: #8D99AE;
        color: black; 
        border-radius: 5px;
        cursor: pointer;
        border: none; /* Ensure no border */
    }
    .next-btn {
        font-size: 20px;
        padding: 10px;
        margin: 10px;
        background-color: #8D99AE;
        color: black; 
        border-radius: 5px;
        cursor: pointer;
        border: none; /* Ensure no border */
    }
    .login-btn {
        font-family: inherit;
        font-size: 20px;
        background: blue; /* Change the color to blue */
        color: white;
        padding: 0.7em 1em;
        padding-left: 0.9em;
        display: flex;
        align-items: center;
        border: none;
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.2s;
        cursor: pointer;
    }
""") as demo:
    # Welcome Page
    with gr.Column(visible=True) as welcome_page:
        gr.HTML("<div class='avatar-guidance-title'>Welcome to Avatar Guidance</div>")
        error_message = gr.Markdown(value="", visible=True)
        with gr.Row():
            with gr.Column(scale=1):
                doc_input = gr.File(label="Upload PDF Document", file_types=[".pdf"], elem_classes="upload-doc")
                img_input = gr.File(label="Upload Image", file_types=[".jpg", ".jpeg", ".png"], elem_classes="upload-img")
                caption_input = gr.Textbox(label="Image Caption", placeholder="Enter caption here")
                go_to_chatbot_button = gr.Button("Go to Chatbot Page", elem_classes="submit-btn")



    # Chatbot Page
    with gr.Column(visible=False) as chatbot_page:
        gr.HTML("<div class='avatar-guidance-title'>Avatar Guidance Chatbot</div>")
        chatbot = gr.Chatbot(elem_classes="chatbox")
        text_input = gr.Textbox(placeholder="Type your message here")
        submit_button = gr.Button("Submit", elem_classes="submit-btn")
        with gr.Row():
            previous_button = gr.Button("Previous", elem_classes="previous-btn", visible=False)
            next_button = gr.Button("Next", elem_classes="next-btn", visible=False)
        go_to_welcome_button = gr.Button("Go to Welcome Page", elem_classes="submit-btn")

    # Define click handler for the go to chatbot button
    go_to_chatbot_button.click(navigate_to_chatbot, 
                               inputs=[doc_input, img_input], 
                               outputs=[welcome_page, chatbot_page, error_message, doc_input, img_input])

    # Define click handler for the go to welcome button
    go_to_welcome_button.click(lambda: (gr.update(visible=True), gr.update(visible=False)), 
                               inputs=[], 
                               outputs=[welcome_page, chatbot_page])

    # Define click handler for the submit button
    submit_button.click(fn=process_input, inputs=[doc_input, img_input, caption_input, text_input], outputs=[chatbot, previous_button, next_button])

    # Define click handlers for previous and next buttons
    previous_button.click(previous_image, inputs=[], outputs=[chatbot, previous_button, next_button])
    next_button.click(next_image, inputs=[], outputs=[chatbot, previous_button, next_button])

    # Launch the Gradio interface
    demo.launch(auth=("admin", "pass1234"), share=True)
