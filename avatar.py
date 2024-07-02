import gradio as gr
from PIL import Image
import base64
from io import BytesIO

# Global state to keep track of current image index and chat history
current_image_index = 0
images = []
chat_history = []

# Function to process input and simulate a response
def process_input(doc, img, caption, message):
    global images, chat_history

    if doc:
        response = f"Received document: {doc.name}"
    elif img:
        response = f"Received image: {img.name}"
        # If an image is uploaded, store it in images list
        img_data = Image.open(img)
        images.append((img_data, caption or "No caption provided"))
    else:
        response = f"Processing your message: {message}"

    # If images list is empty, create dummy images
    if not images:
        create_dummy_images()

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
        <div style="text-align:center;">
            <img src="data:image/png;base64,{img_str}" style="max-width:100px; max-height:100px; border-radius:5px;">
            <br><span>{caption}</span>
        </div>
        """

        chat_history_display.append((None, img_html))
    
    # Update visibility of navigation buttons
    previous_visible = next_visible = bool(images)

    return chat_history_display, gr.update(visible=previous_visible), gr.update(visible=next_visible)

# Function to create dummy images
def create_dummy_images():
    global images
    image1 = Image.new('RGB', (100, 100), color='red')
    image2 = Image.new('RGB', (100, 100), color='green')
    image3 = Image.new('RGB', (100, 100), color='blue')

    # Create captioned images
    images.extend([
        (image1, "This is a red square"),
        (image2, "This is a green square"),
        (image3, "This is a blue square"),
    ])

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
    .nav-btn {
        font-size: 20px;
        padding: 10px;
        margin: 10px;
        background-color: #8D99AE;
        color: black;
        border-radius: 5px;
        cursor: pointer;
    }
""") as demo:
    # Welcome Page
    with gr.Column(visible=True) as welcome_page:
        gr.HTML("<div class='avatar-guidance-title'>Welcome to Avatar Guidance</div>")
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
            previous_button = gr.Button("Previous", elem_classes="nav-btn", visible=False)
            next_button = gr.Button("Next", elem_classes="nav-btn", visible=False)
        go_to_welcome_button = gr.Button("Go to Welcome Page", elem_classes="submit-btn")

    # Define click handler for the go to chatbot button
    go_to_chatbot_button.click(lambda: (gr.update(visible=False), gr.update(visible=True)), 
                               inputs=[], 
                               outputs=[welcome_page, chatbot_page])

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
    demo.launch(auth=("admin", "pass1234"),share=True)
