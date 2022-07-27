FROM python:3.9

WORKDIR /fastapi
COPY ./requirements.txt /fastapi/requirements.txt
COPY ./app /fastapi/app
COPY ./app/botpress_secrets.py /fastapi/app/botpress_secrets.py
COPY ./app/rasa_secrets.py /fastapi/app/rasa_secrets.py
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.chatbotapi:app", "--host", "0.0.0.0", "--port", "3001"]