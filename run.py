from fastapi import FastAPI
import gradio as gr
from avatar import demo

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Gradio app is running at /gradio'}

app = gr.mount_gradio_app(app, demo, path='/gradio')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Make sure this line binds to 0.0.0.0

