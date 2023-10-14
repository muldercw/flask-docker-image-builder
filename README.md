# Flask Docker Image Builder

A Flask-based web application for streamlined Docker image creation tailored for object detection using Haar Cascade models. This user-friendly tool allows you to select a Haar Cascade model and specify an exposed port. The application dynamically generates a Docker image with a corresponding Dockerfile and a Python script for image processing.

## Features

- User-friendly web interface for selecting Haar Cascade models and setting the exposed port.
- Automatic Docker image generation with a Dockerfile.
- Simplified setup for object detection tasks.

## Prerequisites

- Python 3.x
- Docker

## Usage

1. Clone this repository.

2. Run the Flask application:

    ```bash
    python app.py
    ```

3. Access the web interface at `http://localhost:5000` in your web browser.

4. Choose a Haar Cascade model and specify the exposed port.

5. Click the "Generate Docker Image" button to initiate Docker image creation.

6. After the image is built, download the Dockerfile and run the Docker image.

## Contributions

Contributions are welcome! Feel free to open issues or submit pull requests to improve this tool.

## License

This project is licensed under the [GNU General Public License (GPL)](LICENSE) - see the [LICENSE](LICENSE) file for details.

Happy object detection!
