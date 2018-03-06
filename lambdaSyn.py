import requests
import json

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Synonyms. " \
                    "You can know the synonyms of any word! " \
                    "Just say, tell me synonyms of whatever word you like."
                    
    reprompt_text = "If you want synonyms of the word amazing, say " \
                    "synonyms of amazing. Now you try!" 
                    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    
    card_title = "Session Ended"
    speech_output = "Have a nice day! " \
                    "Come back for more synonyms! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
		
		
def synonyms_are(intent, session):
    
    card_title = "Synonyms"
    should_end_session = False
    
    
    if 'value' not in intent['slots']['Word']:
        speech_output = "I am not sure what word you asked for. Please try again."
        reprompt_text = "You can ask for synonyms by saying, tell me synonyms of amazing."
    else:
        word = intent['slots']['Word']['value']
        str = ""

        if word in session_attributes:

            length = len(session_attributes[word])
            for i in range(0,length-1):
                str = str + session_attributes[word][i] + ", "
            str = str+ session_attributes[word][length-1]        
    
            speech_output = "Some synonyms of " + word + " are " + str + "."
            reprompt_text = ""
            
        else:

            parameters = {"ml": word}
            response = requests.get("https://api.datamuse.com/words",params=parameters)

            if response.status_code == 200:
                pyobj = json.loads(response.content)

                length = len(pyobj)

                if length == 0:
                    speech_output = "Sorry, I could not find synonyms for that word. Please try again."
                    reprompt_text = "Try again by saying, tell me synonyms of happy."

                else:
                    if length > 15:
                        length = 15
        
                    l1 = []
                    for i in range(0,length):
                        l1.append(pyobj[i]['word'])
            
                    session_attributes[word] = l1
                    for i in range(0,length-1):
                        str = str + session_attributes[word][i] + ", "
                    str = str+ session_attributes[word][length-1]        
    
                    speech_output = "Some synonyms of " + word + " are " + str + "."
                    reprompt_text = ""

            else:

                speech_output = "Sorry, I could not find synonyms for that word. Please try again."
                reprompt_text = "Try again by saying, tell me synonyms of happy."
                        
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    session_attributes = {}

def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    if intent_name == "SynonymsAreIntent":
        return synonyms_are(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")
        
def on_session_ended(session_ended_request, session):
    session_attributes = {}

# --------------- Main handler ------------------

session_attributes = {}

def lambda_handler(event, context):
    
    if event['session']['new']:
	    on_session_started({'requestId': event['request']['requestId']},event['session'])
		
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
