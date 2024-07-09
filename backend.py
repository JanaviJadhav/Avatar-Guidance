import json
import requests
import os

def get_documents(image_path, image_caption, pdf_path):
    url = "http://localhost:8000/qdrant/aavatar_guidance_addPDF"
    files = []
    pdf_file_name = os.path.basename(pdf_path)
    img_file_name = os.path.basename(image_path)
    files.append(('file', (pdf_file_name, open(pdf_path, 'rb'), 'application/pdf')))
    files.append(('base_image', (img_file_name, open(image_path, 'rb'), 'image/jpeg')))
    headers = {'accept': 'application/json'}
    response_docs = requests.post(url, params={"desc_str": image_caption}, headers=headers, files=files)
    return response_docs.json()

def run_docbot(query, pdf_file_name):
    url = "http://localhost:8000/qdrant/aavatar_guidance_response"
    headers = {'accept': 'application/json'}
    params = {"queryText": query, "filename": pdf_file_name}
    response_json_docbot = requests.post(url, params=params, headers=headers)
    return response_json_docbot.json()

def run_synthvision(docbot_output_json):
    path = "docbot_output_temp.json"
    with open(path, 'w') as fp:
        json.dump(docbot_output_json, fp)
    abs_path = os.path.abspath(path)
    url = "http://localhost:5000/api/synthvision/service"
    files = [('data', (path, open(abs_path, 'rb'), 'application/json'))]
    response = requests.post(url, files=files)
    return response.json()

def post_processing(response):
    gradio_output_tuple = []
    for key, value in response["multimodal recipe"].items():
        gradio_output_tuple.append([value[1], value[2]])
    return tuple(gradio_output_tuple)

def bot(query, pdf_path):
    pdf_file_name = os.path.basename(pdf_path)
    docbot_output_json = run_docbot(query, pdf_file_name)
    dalle_output_json = run_synthvision(docbot_output_json)
    gradio_response = post_processing(dalle_output_json)
    return gradio_response
