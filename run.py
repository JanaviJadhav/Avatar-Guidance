from fastapi import FastAPI
import gradio as gr
from avatar import demo
app =FastAPI
@app.get('/')
async def root():
    return 'Gradio app is ruuning at /gradio',200
app=gr.mount_gradio_app(app ,demo,path='/gradio')
