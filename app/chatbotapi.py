from .botpress_secrets import secrets as botpress_secrets
from .rasa_secrets import secrets as rasa_secrets
from fastapi import FastAPI, Request
from time import time

import logging
import requests

LOGGER = logging.getLogger(__name__)

app = FastAPI()

chatbot = "BOTPRESS"

@app.get('/startsession')
async def startSession(request: Request):
    '''
    This endpoint is used to start a chatbot session. The session start depends on the variable {chatbot}. It can be
    either RASA or BOTPRESS but can be extended by other Chatbot Frameworks.
    :param request: We do need the participant_uuid to generate a suitable session_uuid. The session_uuid is just a
    combination of the participant_uuid and the current timestamp.
    This is currently needed, because we aren't saving the dialog state when we are closing the app.
    It will probably be removed in the future.
    :return: If the chatbot is RASA, we are only returning {"session_uuid": <session_uuid>}. If the chatbot is BOTPRESS,
    we are returning  {"jwt": <jwt>, "session_uuid": <session_uuid>} since the JWT-Token is needed for authorization.
    '''
    session_credentials = {"test":"this should not be printed..."}
    body = await request.json()
    participant_uuid = body['participant_uuid']
    if chatbot is "RASA":
        session_uuid = __getSessionUuId(participant_uuid)
        session_credentials =  {"session_uuid": session_uuid}
    elif chatbot is "BOTPRESS":
        session_uuid = __getSessionUuId(participant_uuid)
        host = botpress_secrets.get('IP')
        port = botpress_secrets.get('PORT')
        pw = botpress_secrets.get('PW')
        email = botpress_secrets.get('EMAIL')

        auth_url = 'http://' + host + ':' + port + '/api/v1/auth/login/basic/default';
        auth_payload = {'email': email, 'password': pw}

        response = requests.post(auth_url, json=auth_payload)

        session_credentials = {"jwt": response.json()['payload']['jwt'], "session_uuid": session_uuid}
    return session_credentials

@app.get('/intervention')
async def getInterventionResponse(request: Request):
    '''
    By calling this endpoint you are sending a message to the chosen chatbot to continue it's intervention
    :param request: You MUST provide the following 2 body parameters: msg and session_credentials. If the Chatbot Framework
    is Botpress, we also need the JWT-Token which is provided in the Header.
    :return: The parsed Intervention answer.
    '''
    body = await request.json()

    msg = body['msg']
    session_uuid = body['session_uuid']

    if chatbot is "RASA":
        return __sendMessageToRasa(msg, session_uuid)
    elif chatbot is "BOTPRESS":
        jwt = request.headers.get('jwt')
        return __sendMessageToBotpress(msg, session_uuid, jwt)

@app.get('/faq')
async def getFaqResponse(request: Request):
    '''
    By calling this endpoint you are sending a message to the chosen chatbots faq. This will start a new session with
    a new session_uuid which is a combination of the session_uuid and "_faq" to prevent us from interrupting the
    current intervention.
    :param request: You MUST provide the following 2 body parameters: msg and session_credentials. If the Chatbot Framework
    is Botpress, we also need the JWT-Token which is provided in the Header.
    :return: The parsed FaQ answer.
    '''
    body = await request.json()

    msg = body['msg']
    session_uuid = body['session_uuid']

    if chatbot is "RASA":
        return __sendMessageToRasa(msg, session_uuid + "_faq")
    elif chatbot is "BOTPRESS":
        jwt = request.headers.get('jwt')
        return __sendMessageToBotpress(msg, session_uuid + "_faq", jwt)

@app.get("/")
async def greet():
    '''
    Method to check if this application is up and running.
    :return: A message to see if the ChatbotParser is up and running.
    '''
    return {"msg":"ChatbotParser is up and running!"}

def __getSessionUuId(participant_uuid):
    '''
    A function to generate a new session_uuid
    :param participant_uuid: participant_uuid
    :return: a new session_uuid
    '''
    return participant_uuid+"_"+str(time())

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

    answer = __parseResponse(data)
    return answer

def __sendMessageToRasa(msg, session_uuid):
    host = rasa_secrets.get('IP')
    port = rasa_secrets.get('PORT')
    token = rasa_secrets.get('TOKEN')

    msg_url = "http://" + host + ":" + port + "/webhooks/rest/webhook?token=" + token

    payload = {"sender": session_uuid, "message": msg}

    response = requests.post(msg_url, json=payload)

    data = response.json()

    answer = __parseResponse(data)
    return answer

def __parseResponse(data):
    answer = {}
    text = ''
    counter = 0
    answer['type'] = 'message'
    answer['data'] = {}
    answer['data']['done'] = 'true'
    answer['data']['flow'] = 'default'
    for element in data:
        answer['data']['answer_type'] = 'text'
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