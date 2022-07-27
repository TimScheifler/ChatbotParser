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
Used to greet you :)

### /jwt
By calling '/jwt' you are requesting an 'JWT-Token', which is required for further communication between the backend and botpress.
So we have to call it first before starting a dialogue with botpress.
No request body needed.

### /botpress
By calling '/botpress' you are sending a message to botpress. You HAVE to provide the following 2 body parameters: msg and session_uuid
which is the participant_uuid + a timestamp. This is currently needed, because we aren't saving the dialog state when we are closing the app. 
It will probably be deprecated in the future. Botpress does need the 'JWT-Token' for authentication, so we need to add it to our request header.

### /botpress/faq
'/botpress/faq' is almost the same as '/botpress'. The only difference is that we are starting a new session for the user so that we won't get conflicts
when switching between interventions and faq mode.



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