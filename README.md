# Chatbot Parser

This parser is used to parse the generated format from rasa and botpress into the needed format of eLan. You can extend
it for other chatbot frameworks aswell!


## Secrets
You probably do not want to show everything to the world. For that we are using files called 'botpress_secrets.py'
and 'rasa_secrets.py' which you have to create in the '/app' module.

### botpress_secrets.py:
```
secrets = {
    'IP':       <IP_BOTPRESS>,
    'PORT':     <PORT_BOTPRESS>,
    'EMAIL':    <ADMIN_EMAIL_BOTPRESS>,
    'PW':       <ADMIN_PW_BOTPRESS,
    'BOT':      <BOT_NAME>
}
```

### rasa_secrets.py:
```
secrets = {
    'IP':       <IP_RASA>,
    'PORT':     <PORT_RASA>,
    'TOKEN':    <TOKEN>,
}
```

## Executing the project

Building the Docker image
```
docker build -t <image_name> . 
```
Running the Docker Container
```
docker run -p 3001:3001 <image_name>
```

## Endpoints
### /
Method to check if this application is up and running.

### /startsession
This endpoint is used to start a chatbot session. The session start depends on the variable {chatbot}. It can be
either RASA or BOTPRESS but can be extended by other Chatbot Frameworks.

We do need the participant_uuid to generate a suitable session_uuid. The session_uuid is just a
combination of the participant_uuid and the current timestamp.
This is currently needed, because we aren't saving the dialog state when we are closing the app.
It will probably be removed in the future.

If the chatbot is RASA, we are only returning {"session_uuid": <session_uuid>}. 

If the chatbot is BOTPRESS, we are returning  {"jwt": <jwt>, "session_uuid": <session_uuid>} since the JWT-Token is needed for authorization.

### /intervention
By calling this endpoint you are sending a message to the chosen chatbot to continue it's intervention

You MUST provide the following 2 body parameters: msg and session_credentials. If the Chatbot Framework is Botpress, we also need the JWT-Token which is provided in the Header.

It is returning the parsed intervention answer.

### /faq
By calling this endpoint you are sending a message to the chosen chatbots faq. This will start a new session with
a new session_uuid which is a combination of the session_uuid and "_faq" to prevent us from interrupting the
current intervention.

You MUST provide the following 2 body parameters: msg and session_credentials. If the Chatbot Framework
is Botpress, we also need the JWT-Token which is provided in the Header.

This endpoint is returning our FaQ answer and has no influence on our intervention.



## Response Format
The response format looks like this:
```
{
    "type": "message",
    "data": {
        "done": <BOOLEAN>,
        "flow": <DEFAULT/FLOW_NAME>,
        "answer_type": "text",
        "message": <CHATBOT_RESPONSE>
    }
}
```
**done:** is needed as an indicator if we can continue with the next flow on eLan

**flow:** the name of the next flow. If there is no matching flow in eLan, eLan will follow the default flow 
(typically retrying to get a correct value)

**message:** the response of the chatbot

**type** and **answer_type** are currently hardcoded, because eLan is only using the chatbot for NLU of textmessages.
Images, buttons, videos and so on are managed by the Dialog Management.