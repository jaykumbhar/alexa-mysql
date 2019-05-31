import json
import mysql.connector
from mysql.connector import Error
def ConnecctMysql():
    try:
        # mySQLconnection = mysql.connector.connect(host='XX.XX.XX.X',database='alexaTest',user='root',password='Paassword')
        mySQLconnection = mysql.connector.connect(host='3.80.151.95',database='alexaTest',user='root',password='123')
        return mySQLconnection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return False
def fetchProducts():
    mySQLconnection = ConnecctMysql()
    sql_select_Query = "select name from product"
    cursor = mySQLconnection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    Player_LIST = records
    cursor.close()
    mySQLconnection.close()
    return Player_LIST
def ProductContryWisePrice(product,country):
    if product is not None and country is not None:
        Price = False
        mySQLconnection = ConnecctMysql()
        sql_select_Query = 'select id from product where name like "%'+product+'%"'
        cursor = mySQLconnection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        recordslist_lower = [w[0] for w in records]
        # print recordslist_lower
        if records:
            sql_select_Query = 'select price from pack where product_id ='+ str(recordslist_lower[0]) + ' and contry like "%'+ str(country) +'%"'
            cursor.execute(sql_select_Query)
            mytestp = cursor.fetchall()
            Price = [w[0] for w in mytestp]
        cursor.close()
        mySQLconnection.close()
        if Price:
            return Price[0]
        return Price
    return False


def ProductDetailsInformation(product):
    info = False
    mySQLconnection = ConnecctMysql()
    sql_select_Query = 'select id from product where name like "%'+str(product)+'%"'
    cursor = mySQLconnection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    recordslist_lower = [w[0] for w in records]
    # cursor.close()
    if records:
        sql_select_Query2 = 'select description,contry from pack where product_id ='+ str(recordslist_lower[0]) 
        cursor.execute(sql_select_Query2)
        mytestp = cursor.fetchall()
        # info = [w for w in mytestp]
        info = []
        for w in mytestp:
            info.append({w[1]:w[0]})
            # for m in w:
                # print m
                # info.append(m)
    cursor.close()
    mySQLconnection.close()
    return info
    # return False

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
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

def on_end():
    print("Session Ended.")

def intent_scheme(event):
    intent_name = event['request']['intent']['name']
    if intent_name == "productcheck":
        return get_Product(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    # elif intent_name in ["AMAZON.AMAZON.YesIntent"]:
    #     return productDetails(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


def get_Product(event):
    # try:
    if 'value' in event['request']['intent']['slots']['products'] and event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
        Product_name = event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    else:
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong technology."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False) 
    null = None

    if 'value' in (event['request']['intent']['slots']['countries']) :
        country_name = event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    else:
        information = ProductDetailsInformation(Product_name)
        if information:
            contries = [x.keys()[0] for x in information]
            for data in information:
                for con in contries:
                    if con in data.keys():
                        mymsg = data[con]

            contriesstring = ','.join(map(str, contries))
            mreponse = 'As per Your selected Product '+ str(Product_name) +  " is " + str(mymsg)+ "and this Product Avalible in "+str(contriesstring) 
            
            # mreponse = "As per Your selected Product " + str(Product_name) +  " is " + str(information[0])+ "and this Product Avalible in "+str(information[1]) 
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "You've picked " + str(Product_name .lower())
            card_TITLE = "You've picked " + str(Product_name .lower())
            return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False)
        else:
            wrongname_MSG = "Sorry This product is not availble as per request."
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong technology."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)
    
    checkPrice = ProductContryWisePrice(Product_name ,country_name)
    if checkPrice:
        myreponse = "As per Your selected Product " + str(Product_name) + " in " + str(country_name) + " price is " + str(checkPrice)
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "You've picked " + str(Product_name .lower())
        card_TITLE = "You've picked " + str(Product_name .lower())
        return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE,reprompt_MSG, False)
    else:
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong technology."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

def stop_the_skill(event):
    stop_MSG = "Thank you. Bye! we will meet after some time"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True)


def assistance(event):
    assistance_MSG = "Please give me a product name and contry name so I can give you a proper information regarding Product"
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


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


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title,
                                                                              reprompt_text, value)
    return response_dict

# if __name__== "__main__":
# #     # print(ProductContryWisePrice('cipla','india'))
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
