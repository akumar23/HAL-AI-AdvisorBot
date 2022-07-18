FROM python:3.7

WORKDIR /HAL-final
ADD . /HAL-final

RUN pip install -r requirements.txt

CMD [ "python", "runChatbot.py" ]