# Chatbot Parser

This parser is used to parse the generated format from rasa and botpress into the needed format of eLan. You can extend
it for other chatbot frameworks aswell!


## Secrets
You probably do not want to show everything to the world. For that we are using files called 'botpress_secrets.py'
and 'rasa_secrets.py' which you have to create in the '/app' module.

### botpress_secrets.py:
```
secrets = {
    'IP':   <IP_BOTPRESS>,
    'PORT': <PORT_BOTPRESS>,
    'EMAIL':<ADMIN_EMAIL_BOTPRESS>,
    'PW':   <ADMIN_PW_BOTPRESS,
    'BOT':  <BOT_NAME>
}
```

### rasa_secrets.py:
```
TODO
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

## Request Format

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