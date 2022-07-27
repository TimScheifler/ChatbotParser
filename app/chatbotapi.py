from .botpress_secrets import secrets as botpress_secrets
from .rasa_secrets import secrets as rasa_secrets
from fastapi import FastAPI, Request

import logging
import requests

LOGGER = logging.getLogger(__name__)

app = FastAPI()

'''
This function is used to send a question to Botpress. It is using another UUID then the normal user to differenciate between both.
It is possible to just answer these questions by using the FaQ function of Botpress itself, but it is possible, that a question
will need more context (so more messages back and forth). So it might be better to handle them like a dialogue.
'''

@app.get("/botpress/faq")
async def getBotpressFaqResponse(request: Request):
    body = await request.json()

    jwt = request.headers.get('jwt')
    msg = body['msg']
    session_uuid = body['session_uuid']

    return __sendMessageToBotpress(msg, session_uuid + '_faq', jwt)

'''
This function is used to send messages back and forth between the backend and Botpress.
'''

@app.get("/botpress/intervention")
async def getBotpressInterventionResponse(request: Request):
    body = await request.json()

    jwt = request.headers.get('jwt')
    msg = body['msg']
    session_uuid = body['session_uuid']
    return __sendMessageToBotpress(msg, session_uuid, jwt)

@app.get("/botpress/jwt")
async def getBotpressJwt():
    host = botpress_secrets.get('IP')
    port = botpress_secrets.get('PORT')
    pw = botpress_secrets.get('PW')
    email = botpress_secrets.get('EMAIL')

    auth_url = 'http://' + host + ':' + port + '/api/v1/auth/login/basic/default';
    auth_payload = {'email': email, 'password': pw}

    response = requests.post(auth_url, json=auth_payload)

    return { "jwt":response.json()['payload']['jwt']}

@app.get("/rasa/intervention")
async def getRasaInterventionResponse(request: Request):
    body = await request.json()

    msg = body['msg']
    session_uuid = body['session_uuid']

    return __sendMessageToRasa(msg, session_uuid)

@app.get("/rasa/faq")
async def getRasaFaqResoinse(request: Request):
    body = await request.json()

    msg = body['msg']
    session_uuid = body['session_uuid']

    return __sendMessageToRasa(msg, session_uuid + '_faq')

@app.get("/")
async def greet():
    return {"msg":"Hello Traveller! :)"}

#TODO es gibt viele Überschneidungungen zwischen __sendMessageToBotpress und __sendMessageToRasa. Diese sollten bestmöglichst entfernt werden.
def __sendMessageToBotpress(msg, session_uuid, jwt):
    host = botpress_secrets.get('IP')
    port = botpress_secrets.get('PORT')
    bot_name = botpress_secrets.get('BOT')

    LOGGER.warning("TEEEST: " + msg + " " + session_uuid + " " + jwt)

    msg_url = 'http://' + host + ':' + port + '/api/v1/bots/' + bot_name + '/converse/' + session_uuid + '/secured?include=nlu'

    msg_payload = {'type': 'text', 'text': msg}
    header = {'Authorization': 'Bearer ' + jwt}

    response = requests.post(msg_url, json=msg_payload, headers=header)
    response_json = response.json()
    LOGGER.warning("RESPONSE: " + str(response_json))
    data = response.json()['responses']
    answer = {}
    text = ''
    counter = 0
    answer['type'] = 'message'
    answer['data'] = {}
    answer['data']['done'] = 'true'
    answer['data']['flow'] = 'default'
    for element in data:
        answer['data']['answer_type'] = element['type']
        answer['data']['done'] = 'true'
        if element['text'] == '$end':
            if '---' in text:
                answer['data']['flow'] = text.split('---')[-1]
            else:
                answer['data']['flow'] = text
                text = ""
        else:
            answer['data']['done'] = 'false'
            if counter > 0:
                text = text + '---'
            text = text + element['text']
        counter = counter + 1

    answer['data']['message'] = text
    return answer

def __sendMessageToRasa(msg, session_uuid):
    host = rasa_secrets.get('IP')
    port = rasa_secrets.get('PORT')
    token = rasa_secrets.get('TOKEN')

    url = "http://" + host + ":" + port + "/webhooks/rest/webhook?token=" + token

    payload = {"sender": session_uuid, "message": msg}

    response = requests.post(url, json=payload)

    data = response.json()

    answer = {}
    text = ''
    counter = 0
    answer['type'] = 'message'
    answer['data'] = {}
    answer['data']['done'] = 'true'
    answer['data']['flow'] = 'default'

    for element in data:
        answer['data']['answer_type'] = 'text'
        if element['text'] == '$end':
            answer['data']['done'] = 'true'
            if '---' in text:
                answer['data']['flow'] = text.split('---')[-1]
            else:
                answer['data']['flow'] = text
        else:
            answer['data']['done'] = 'false'
            if counter > 0:
                text = text + '---'
            text = text + element['text']
        counter = counter + 1

    answer['data']['message'] = text
    return answer
