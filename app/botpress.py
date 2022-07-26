from .botpress_secrets import secrets
from time import time
from fastapi import FastAPI, Header
from typing import Union

import requests

app = FastAPI()

'''
This function is used to send a question to Botpress. It is using another UUID then the normal user to differenciate between both.
It is possible to just answer these questions by using the FaQ function of Botpress itself, but it is possible, that a question
will need more context (so more messages back and forth). So it might be better to handle them like a dialogue.
'''

@app.get("/botpress/faq")
async def getBotpressFaqResponse(msg, session_uuid, jwt: Union[str, None] = Header(default=None)):
    return getBotpressResponse(msg, session_uuid + "_faq", jwt)


'''
This function is used to send messages back and forth between the backend and Botpress.
'''

@app.get("/botpress")
async def getBotpressResponse(msg, session_uuid, jwt: Union[str, None] = Header(default=None)):
    host = secrets.get('IP')
    port = secrets.get('PORT')
    bot_name = secrets.get('BOT')

    msg_url = 'http://' + host + ':' + port + '/api/v1/bots/' + bot_name + '/converse/' + session_uuid + '/secured?include=nlu'

    msg_payload = {'type': 'text', 'text': msg}
    header = {'Authorization': 'Bearer ' + jwt}

    response = requests.post(msg_url, json=msg_payload, headers=header)
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


@app.get("/jwt")
async def getJwt():
    host = secrets.get('IP')
    port = secrets.get('PORT')

    auth_url = 'http://' + host + ':' + port + '/api/v1/auth/login/basic/default';
    auth_payload = {'email': secrets.get('EMAIL'), 'password': secrets.get('PW')}

    response = requests.post(auth_url, json=auth_payload)

    return { "jwt":response.json()['payload']['jwt']}


@app.get("/sessionuuid")
async def getSessionUuId(participant_uuid: str):
    return {"session_uuid":participant_uuid + "_" + str(time())}

@app.get("/")
async def greet():
    return {"msg":"Hello World!"}