from flask import Flask, request, render_template_string, send_file
import os

app = Flask(__name__)
haar_cascade_folder = 'haarcascade'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_model = request.form['model']
        exposed_port = request.form['port']
        docker_image_name = generate_image(selected_model, exposed_port)
        return send_file(f'{docker_image_name}.tar', as_attachment=True)
    models = list_available_models(haar_cascade_folder)
    return render_template_string(get_index_template(), models=models)

def list_available_models(folder):
    xml_files = [file for file in os.listdir(folder) if file.endswith('.xml')]
    return xml_files

def get_index_template():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Docker Builder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            text-align: center;
        }
        h1 {
            color: #333;
        }
        form {
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 20px;
            width: 400px;
            margin: 0 auto;
        }
        label {
            display: block;
            font-weight: bold;
        }
        select, input {
            width: 150px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 3px;
            margin-bottom: 10px;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer.
        }
        button:hover {
            background-color: #0056b3;
        }
        h2 {
            margin-top: 20px;
            font-size: 20px;
        }
        ins {
            position: fixed;
            width: 50%;
            height: 300px;
            left: 50%;
            margin: 0 0 0 -25%
        }
        ol {
            text-align: left;
            margin-left: 400px;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
            font-family: monospace;
            margin-bottom: 20px;
        }
        .docker-logo {
            left: 50%;
            max-width: 100px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="docker-logo">
        <svg xmlns="http://www.w3.org/2000/svg" aria-label="Docker" role="img" viewBox="0 0 512 512">
            <rect width="512" height="512" rx="15%" fill="#ffffff"/>
            <path stroke="#066da5" stroke-width="38" d="M296 226h42m-92 0h42m-91 0h42m-91 0h41m-91 0h42m8-46h41m8 0h42m7 0h42m-42-46h42"/>
            <path fill="#066da5" d="m472 228s-18-17-55-11c-4-29-35-46-35-46s-29 35-8 74c-6 3-16 7-31 7H68c-5 19-5 145 133 145 99 0 173-46 208-130 52 4 63-39 63-39"/>
        </svg>
    </div>
    <h1>Select Model for Docker Creation</h1>
    <form method="POST">
        <label for "model">Select a model:</label>
        <select name="model" id="model">
            {% for model in models %}
                <option value="{{ model }}">{{ model }}</option>
            {% endfor %}
        </select>
        <label for="port">Exposed Port:</label>
        <input type="number" name="port" id="port" value="8080">
        <br>
        <button type="submit">Generate Docker Image</button>
    </form>
    <h2>Instructions:</h2>
    <ins>
    <ol>
        <li>Choose a model from the list above.</li>
        <li>Specify the port you want to expose (default is 8080).</li>
        <li>Click the "Generate Docker Image" button to initiate Docker image creation.</li>
        <li>After the image is built, download the Dockerfile.</li>
        <li>To run the Dockerfile, run the following commands in your terminal:</li>
    </ol>
    <code id="codeBlock"></code>
    </ins>
</body>
<script>
    function updateCodeBlock() {
        var selectedModel = document.getElementById("model").value;
        var exposedPort = document.getElementById("port").value;
        var codeBlock = document.getElementById("codeBlock");
        var code = `docker load -i ${selectedModel}_image.tar<br>` +
                   `docker run -p ${exposedPort}:${exposedPort} ${selectedModel}_image:latest`;
        codeBlock.innerHTML = code;
    }
    document.getElementById("model").addEventListener("change", updateCodeBlock);
    document.getElementById("port").addEventListener("input", updateCodeBlock);
    updateCodeBlock();
</script>
</html>
"""

def generate_image(selected_model, exposed_port):    
    dockerfile_content = f"""
FROM python:3.8-slim
WORKDIR /app
COPY haarcascade/{selected_model} /app/{selected_model}
COPY detect.py detect.py
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
RUN pip install flask numpy opencv-python-headless
EXPOSE {exposed_port}
CMD ["python", "detect.py"]
"""

    docker_image_name = f'{selected_model}_image'
    with open("Dockerfile", "w") as dockerfile:
        dockerfile.write(dockerfile_content)

    model_script = f"""
from flask import Flask, request, send_file, render_template_string
import cv2
import numpy as np
app = Flask(__name__)

port = {exposed_port}  # Change this to your desired port

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return 'No image file provided', 400
    image_file = request.files['image']
    if image_file.filename == '':
        return 'No selected file', 400
    nparr = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    obj_cascade = cv2.CascadeClassifier('{selected_model}')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    objs = obj_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in objs:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
    output_path = 'output_{selected_model}.jpg'
    cv2.imwrite(output_path, image)
    return send_file(output_path, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return process_image()
    upload_form = '''<!DOCTYPE html>
<html>
<head>
    <title>Image Upload</title>
</head>
<body>
    <h1>Image Upload</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <input type="submit" value="Upload and Process">
    </form>
</body>
</html>'''

    return render_template_string(upload_form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)

"""
    with open("detect.py", "w") as detect_py:
        detect_py.write(model_script)
    os.system(f"docker build --no-cache -t {docker_image_name} .")
    os.system(f"docker save -o {docker_image_name}.tar {docker_image_name}")
    os.system(f"docker rmi {docker_image_name}")
    os.remove("Dockerfile")
    os.remove("detect.py")
    return docker_image_name

if __name__ == '__main__':
    app.run()