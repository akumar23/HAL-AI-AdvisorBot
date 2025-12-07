# HAL-AI-AdvisorBot
An AI chatbot that gives advice to CMPE and SE students at SJSU.

to get from docker: docker pull mfaryan/hal-final

demo video: https://youtu.be/dVwozVz11ho?t=78

## Requirements

**Python Version: 3.10 - 3.12 (3.11 recommended)**

> **Note:** Python 3.13+ is not currently supported due to ChromaDB dependency compatibility issues. ChromaDB requires `pulsar-client` which is not available for Python 3.13+. Please use Python 3.11 for the best experience.

## Instructions to Run

### Legacy ChatterBot Application
Download or git clone the code and navigate to where the project is downloaded.

Make sure you have python3 and pip3.

then run 'pip3 install -r requirements.txt' to make sure the needed python libraries are installed.

Finally run the code with 'python3 runChatbot.py' and wait for all the training data to be read and go to http://127.0.0.1:5000/

### New RAG-based Application
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 app.py
```
The app runs at http://127.0.0.1:5000/

### Admin Interface
Access at http://127.0.0.1:5000/admin (requires login)
