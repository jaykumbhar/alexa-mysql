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
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)

def on_end():
    print("Session Ended.")

def intent_scheme(event):
    intent_name = event['request']['intent']['name']
    if intent_name == "productcheck":
        return get_Product(event)
    if intent_name == "onlyProduct":
        return getOnlyProductData(event)
    if intent_name == "ProductForAllCountries":
        return GetAllProductInformationWithinCountry(event)
    if intent_name == "CountryWiseAllProducts":
        return GetAllCountryInformationWithinProduct(event)
    if intent_name == "onlyCountry":
        return getOnlyCountryData(event)
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
        wrongname_MSG = "Sorry This country name is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular country_name?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong country_name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False) 
    return getProductCountryWiseDetailsPrice(Product_name,country_name,event)
          
def getOnlyProductData(event):
    Product_name = event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Country' in mytestSession:
            country_name = mytestSession['Country']
            return getProductCountryWiseDetailsPrice(Product_name,country_name,event)
        else:
            mytestSession["Product"]=Product_name
    else:
        mytestSession = {"Product":Product_name }

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
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 0
    Mysenteces = []
    countries = []
    for pack in availabepacks:
        numbercount += 1    
        test = ' '+str(numbercount)+'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
        Mysenteces.append(test)
        countries.append(pack['country'])
    checkPrice = ', '.join(map(str, Mysenteces))
    mdata = [s.lower() for s in countries]
    unique_data = set(mdata)
    countries = list(unique_data)
    contriesstring = ', '.join(map(str, countries))
    mreponse = 'As per Your requested '+str(numbercount)+' packs of '+ str(Product_name) +  " are availble in " + str(contriesstring)+' DO You want to check All Countries information or specific Countries information ?'
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name .lower())
    card_TITLE = "You've picked " + str(Product_name .lower())
    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mytestSession)

def getOnlyCountryData(event):
    country_name = event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    ResponseDataJson = SendCountryDataReq(country_name)

    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Product' in mytestSession:
            Product = mytestSession['Product']
            return getProductCountryWiseDetailsPrice(Product,country_name,event)
        else:
            mytestSession["Country"]=country_name
    else:
        mytestSession = {"Country":country_name }

    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    AllProducts = []
    countries = []
    numbercount = 0
    for pack in availabepacks:
        # test = ' '+str(numbercount)+'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
        # Mysenteces.append(test)
        countries.append(pack['country'])
        AllProducts.append(pack['name'])
        numbercount += 1
    # checkPrice = ' '.join(map(str, Mysenteces))
    mdata = [s.lower() for s in countries]
    product_calculate = [s.lower() for s in AllProducts]
    product_count = set(product_calculate)
    unique_data = set(mdata)
    # countries_count = len(unique_data)
    # countries = list(unique_data)
    # contriesstring = ' '.join(map(str, countries))
    mreponse = 'As per Your requested '+str(country_name)+' '+ str(len(product_count)) +  " products are availble . DO You want to check AllProducts information or specific Product information ?" 
    reprompt_MSG = "Do you want to hear more about AllProducts OR a particular Product ?"
    card_TEXT = "You've picked " + str(country_name .lower())
    card_TITLE = "You've picked " + str(country_name .lower())
    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mytestSession)

def getProductCountryWiseDetailsPrice(Product_name,country_name,event):
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
    numbercount = 0
    packcount =0 
    Mysenteces = []
    for pack in availabepacks:
        if len(availabepacks)>1:
            packcount +=1
        else:
            test = ''+str(numbercount) +'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
            Mysenteces.append(test)
            numbercount += 1
    checkPrice = ', '.join(map(str, Mysenteces))
    if packcount > 1:
        myreponse = "As per Your selected Product " + str(Product_name) + " in " + str(country_name) + " " + str(packcount)+ " Packs are availble Do You want to chek all packs or check a specific pack ? For all packs say Allpacks and For a specific pack give me a pack name or strength of pack so I can tell you the available specific packs."  #+str(event['session']['attributes'])
        mtattribute = event['session']
        if 'attributes' in event['session']:
            packdatacheck = {'country':country_name,'product':Product_name}
            if 'packdatacheck' in event['session']['attributes']:
                event['session']['attributes']['packdatacheck'] = packdatacheck
            else:
                event['session']['attributes']['packdatacheck'] = packdatacheck
                mtattribute = event['session']['attributes']
    else:
        myreponse = "As per Your selected Product " + str(Product_name) + " in " + str(country_name) + " is available in following pack :" + str(checkPrice)#+str(event['session']['attributes'])
        mtattribute = event['session']['attributes'] = {'test':'removed'}

    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name .lower())
    card_TITLE = "You've picked " + str(Product_name .lower())
    
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mtattribute)
  
def GetAllProductInformationWithinCountry(event):
    print "I AM IN GetAllProductInformation"
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Product' in mytestSession:
            Product_name = mytestSession['Product']
        else:
            print e
            wrongname_MSG = "Sorry I didn't Understand Product Name Will You please tell me reapeat Prodcut name."
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong Product."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
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
        ResponseDataJson = json.loads(ResponseData.read())
        availabepacks = ResponseDataJson['data']['information']['availabepacks']
        numbercount = 0
        Mysenteces = []
        countries = []
        for pack in availabepacks:
            numbercount += 1
            test = ' '+str(numbercount)+'. '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
            Mysenteces.append(test)
            countries.append(pack['country'])
        checkPrice = ', '.join(map(str, Mysenteces))
        mdata = [s.lower() for s in countries]
        unique_data = set(mdata)
        countries = list(unique_data)
        contriesstring = ' '.join(map(str, countries))
        mreponse = 'As per Your requested '+str(numbercount)+' packs of '+ str(Product_name) +  " are availble in " + str(contriesstring)
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "You've picked " + str(Product_name .lower())
        card_TITLE = "You've picked " + str(Product_name .lower())
        return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mytestSession)  
    else:
        wrongname_MSG = "Sorry Didn't Find anything Will you please repeat."
        reprompt_MSG = "Do you want to hear more Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
 
def GetAllCountryInformationWithinProduct(event):
    print "I AM IN GetAllCountryInformationWithinProduct"
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Country' in mytestSession:
            country_name = mytestSession['Country']
        else:
            print e
            wrongname_MSG = "Sorry I didn't Understand Country Name Will You please tell me reapeat Country name."
            reprompt_MSG = "Do you want to hear more about a particular Country?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong Country."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
        
        ResponseDataJson = SendCountryDataReq(country_name)
        availabepacks = ResponseDataJson['data']['information']['availabepacks']
        numbercount = 0
        AllProducts = []
        Mysenteces = []
        countries = []
        for pack in availabepacks:
            numbercount += 1
            test = ' '+str(numbercount)+'. '+str(pack['name']) +' : '+str(pack['description'])+' Price For '+str(pack['price_type'])+' is '+str(pack['price'])+' '+str(pack['currency'])
            Mysenteces.append(test)
            countries.append(pack['country'])
            AllProducts.append(pack['name'])
        
        checkPrice = ', '.join(map(str, Mysenteces))
        product_calculate = [s.lower() for s in AllProducts]
        product_count = set(product_calculate)
        # unique_data = set(mdata)
        # countries_count = len(unique_data)
        # countries = list(unique_data)
        # contriesstring = ' '.join(map(str, countries))
        mreponse = 'As per Your requested '+str(country_name)+' '+ str(len(product_count)) +  " products are availble following are detail information "+str(checkPrice) 
        # mreponse = 'As per Your requested '+str(numbercount)+' packs of '+ str(Product_name) +  " are availble in " + str(contriesstring)+str(event['session']['attributes'])

        reprompt_MSG = "Do you want to hear more about AllProducts OR a particular Product ?"
        card_TEXT = "You've picked " + str(country_name .lower())
        card_TITLE = "You've picked " + str(country_name .lower())
        return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE,reprompt_MSG, False,mytestSession)
    else:
        wrongname_MSG = "Sorry Didn't Find anything Will you please repeat."
        reprompt_MSG = "Do you want to hear more Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)


def SendCountryDataReq(country_name):
    url = str(BASEURL)+'countrywiseproductcheck/'+str(country_name)
    print url
    try:
        ResponseData = urllib2.urlopen(url)
    except Exception as e:
        print e
        wrongname_MSG = "Sorry This country is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular country?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong country name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False) 
    ResponseDataJson = json.loads(ResponseData.read())
    return ResponseDataJson


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
