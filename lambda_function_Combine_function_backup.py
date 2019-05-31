import json
import urllib2
BASEURL = 'http://3.80.151.95:6500/api/'

def lambda_handler(event, context):
    # event = event['payload']['content']['invocationRequest']['body']
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()
def on_start():
    print("Session Started.")

def on_launch(event):
    onlunch_MSG = "Hi, welcome to the Our Sysytem. Do You have any query regarding Price of tabet in any countries "#+ ', '.join(
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "Pick a tablet."
    card_TITLE = "Choose a tablet."
    mytestSession = {"favoriteColor": "blue"}
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,mytestSession)

def on_end():
    print("Session Ended.")

def intent_scheme(event):
    intent_name = event['request']['intent']['name']
    if intent_name == "productcheck":
        return get_Product(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


def get_Product(event):
    if 'value' in event['request']['intent']['slots']['products'] and event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
        Product_name = event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    else:
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong technology."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False) 
    if 'value' in (event['request']['intent']['slots']['countries']) or 'resolutions' in event['request']['intent']['slots']['countries']: 
        country_name = event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    else:
        url = str(BASEURL)+'productlistcheck/'+str(Product_name)
        try:
            ResponseData = urllib2.urlopen(url)
        except Exception as e:
            print e
            wrongname_MSG = "Sorry This product is not availble as per request."
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong Product."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
        
        if 'attributes' in event['session']:
            mytestSession = event['session']['attributes']
            mytestSession["Product"]=Product_name
        else:
            mytestSession = {"Product":Product_name }
        ResponseDataJson = json.loads(ResponseData.read())
        availabepacks = ResponseDataJson['data']['information']['availabepacks']
        numbercount = 1
        Mysenteces = []
        countries = []
        for pack in availabepacks:
            test = ' '+str(numbercount)+'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
            Mysenteces.append(test)
            countries.append(pack['country'])
            numbercount += 1
        checkPrice = ' '.join(map(str, Mysenteces))
        mdata = [s.lower() for s in countries]
        unique_data = set(mdata)
        countries = list(unique_data)
        contriesstring = ' '.join(map(str, countries))
        mreponse = 'As per Your requested '+str(numbercount)+' packs of '+ str(Product_name) +  " are availble in " + str(contriesstring)+str(event['session']['attributes'])
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "You've picked " + str(Product_name .lower())
        card_TITLE = "You've picked " + str(Product_name .lower())
        return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mytestSession)
    url = str(BASEURL)+'productcountryPriceCheck/'+str(Product_name)+'/'+str(country_name)
    try:
        ResponseData = urllib2.urlopen(url)
    except Exception as e:
        print e
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 1
    Mysenteces = []
    for pack in availabepacks:
        test = ''+str(numbercount) +'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
        Mysenteces.append(test)
        numbercount += 1
    checkPrice = ' '.join(map(str, Mysenteces))
    myreponse = "As per Your selected Product " + str(Product_name) + " in " + str(country_name) + " is available in following packs :" + str(checkPrice)+str(event['session']['attributes'])
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name .lower())
    card_TITLE = "You've picked " + str(Product_name .lower())
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE,reprompt_MSG, False,False)
        
def stop_the_skill(event):
    stop_MSG = "Thank you. Bye! we will meet after some time"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True,False)


def assistance(event):
    assistance_MSG = "Please give me a product name and contry name so I can give you a proper information regarding Product"
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)


def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)


def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict


def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict


def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value,mytestSession):
    response_dict = {}
    response_dict['version'] = '1.0'
    if mytestSession:       
        print mytestSession 
        response_dict['sessionAttributes'] = mytestSession
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title,
                                                                              reprompt_text, value)
    return response_dict

# if __name__== "__main__":
# print(get_Product(event))
# # #     # print(ProductContryWisePrice('cipla','india'))
# #     # print(fetchProducts())
#     Product_name = 'cipla'
#     information = ProductDetailsInformation(Product_name)
#     contries = [x.keys()[0] for x in information]
#     for data in information:
#         for con in contries:
#             if con in data.keys():
#                 mymsg = data[con]

#     contriesstring = ','.join(map(str, contries))
#     mreponse = 'As per Your selected Product '+ str(Product_name) +  " is " + str(mymsg)+ "and this Product Avalible in "+str(contriesstring) 
#     print(mreponse)
