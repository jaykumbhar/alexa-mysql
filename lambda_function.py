import json
import urllib2
import random

# BASEURL = 'http://3.89.184.128:6500/api/'##Vijay Acoount 
BASEURL = 'http://3.85.238.217:6500/api/'#ashish Acoount 

# BASEURL = 'http://127.0.0.1:8000/api/'

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
    onlunch_MSG = "Hi, welcome to the Our System. Do You have any query regarding Price of tabet in any countries ! You can Say Directly Product Name country Name to check price"  # + ', '.join(
    reprompt_MSG = "I am Reddy to help You, Please Give me a command so I can help you"
    card_TEXT = "Pick a Medicine."
    card_TITLE = "Choose a Medicine."
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, False)

def on_end():
    print("Session Ended.")
    wrongname_MSG = "Sorry I didn't Find Any thing "
    reprompt_MSG = "Please contact System Manager ?"
    card_TEXT = "Use the full form."
    card_TITLE = "Wrong Product."
    return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)

def intent_scheme(event):
    intent_name = event['request']['intent']['name']
    print "I am Insied intent_scheme"
    if intent_name == "productcheck":
        return get_Product(event)
    elif intent_name == "PacksCheck":
        return get_PacksData(event,False)
    elif intent_name == "onlyProduct":
        return getOnlyProductData(event)
    elif intent_name == "ProductForAllCountries":
        return GetAllProductInformationWithinCountry(event)
    elif intent_name == "CountryWiseAllProducts":
        return GetAllCountryInformationWithinProduct(event)
    elif intent_name == "onlyCountry":
        return getOnlyCountryData(event)
    elif intent_name == "onlyRegions":
        return getOnlyRegionsData(event)
    elif intent_name == "GetProductInformation":
        return getTestingProduct(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.YesIntent":
        return yes_continue_the_skill(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


def getTestingProduct(event):
    try:
        url = str(BASEURL) + 'productlist/'
        print url
        ResponseData = urllib2.urlopen(str(url))
    except Exception as e:
        print e
        wrongname_MSG = "Sorry products not availble as per request."
        reprompt_MSG = "Please contact System Manager ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['products']
    Mysenteces = []
    for pack in availabepacks:
        Mysenteces.append(pack['name'])
    mytest = []    
    # random.choice(Mysenteces)
    for i in range(1,6):
        mytest.append(Mysenteces[random.randrange(1,len(Mysenteces)-1)])

    unique_data = set(mytest)
    myuniqueProducts = list(unique_data)
    myProducts = ', '.join(map(str, myuniqueProducts))
    mreponse = 'for your request following Products are availble '+str(myProducts)+' These kind of Products are availble for the demo purpose Please Continue with That .'
    reprompt_MSG = "Are you satisfied with this answer ? "
    card_TEXT = "My Product list "
    card_TITLE = "My Product list"
    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      False)


def get_Product(event):
    print " I am Inside get_Product"
    mtattribute = False
    if 'value' in event['request']['intent']['slots']['products'] and \
            event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['status'][
                'code'] == 'ER_SUCCESS_MATCH':
        Product_name = \
        event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['values'][0][
            'value']['name']
        mtattribute = {'packdatacheck': {'product': Product_name},'Product': Product_name}
    else:
        wrongname_MSG = "Sorry as per requested product is not availble."
        reprompt_MSG = "Please give me Product name ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    if 'value' in event['request']['intent']['slots']['countries'] and event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
        country_name = event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        mtattribute['packdatacheck'].update({'country': country_name})
        mtattribute.update({'Country': country_name})

    elif 'value' in (event['request']['intent']['slots']['regions']) or 'resolutions' in event['request']['intent']['slots']['regions']:
        regions_name = event['request']['intent']['slots']['regions']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        if regions_name:
            mtattribute.update({'regions':regions_name})
            mtattribute['packdatacheck'].update({'regions': regions_name})
            event['session']['attributes']= mtattribute
            return getProductResionWiseDetailsPrice(Product_name, regions_name, event)
    else:
        wrongname_MSG = "Sorry as per requested country or Resion is not availble, Please Give me a Country Name Or Resion name "
        reprompt_MSG = "Please give me country name ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          mtattribute)
    mtattribute = {'packdatacheck': {'product': Product_name,'country': country_name},'Product': Product_name,'Country': country_name}

    if 'value' in (event['request']['intent']['slots']['strength']) or 'resolutions' in event['request']['intent']['slots']['strength']:
        if event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
            strengths_name = event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
            mtattribute = {'packdatacheck': {'product': Product_name,'country': country_name,'strength':strengths_name},'Product': Product_name,'Country': country_name}
            event['session']['attributes'] = mtattribute
            return get_PacksData(event,mtattribute)
        else:
            wrongname_MSG = "Sorry as per requested product with country Strength is not availble, Please Give me a proper Strength Name "
            reprompt_MSG = "Please give me country name ?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong product."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                              mtattribute)
    return getProductCountryWiseDetailsPrice(Product_name, country_name, event)


def getOnlyProductData(event):
    if 'value' in event['request']['intent']['slots']['products'] and \
            event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['status'][
                'code'] == 'ER_SUCCESS_MATCH':
        Product_name = \
        event['request']['intent']['slots']['products']['resolutions']['resolutionsPerAuthority'][0]['values'][0][
            'value']['name']
    else:
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear about more Products ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    if 'attributes' in event['session']:
        if 'Country' in event['session']['attributes']:
            country_name = event['session']['attributes']['Country']
            if country_name:
                return getProductCountryWiseDetailsPrice(Product_name, country_name, event)
    try:
        Product_name = urllib2.quote(Product_name)
        url = str(BASEURL) + 'productlistcheck/' + str(Product_name)
        print url
        ResponseData = urllib2.urlopen(str(url))
        Product_name = urllib2.unquote(Product_name)

    except Exception as e:
        print e
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear about more Products ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 0
    Mysenteces = []
    countries = []
    regions = []
    for pack in availabepacks:
        numbercount += 1
        regions.append(pack['region'])
        countries.append(pack['country'])
    checkPrice = ', '.join(map(str, Mysenteces))
    mdata = [s.lower() for s in countries]
    unique_data = set(mdata)
    countries = list(unique_data)
    rdata = [s.lower() for s in regions]

    unique_R_data = set(rdata)

    regions_numbers = list(unique_R_data)
    if len(regions_numbers) > 1:
        contriesstring = ' , '.join(map(str, regions_numbers))
        mreponse = 'for ' + str(Product_name) +" "+ str(numbercount) + " packs are availble in " + str(contriesstring) + ' Do You want to check  Product information for specific regions ? Say a specific Region Name For example... (Eastern)'
    else:
        mreponse = 'for ' + str(Product_name) +" "+ str(numbercount) + "   packs are availble in " + str(regions_numbers[0]) + ' Region and within ' + str(regions_numbers[0]) + ' Product available on' + str(len(countries)) + ' countries Do You want to check for All For all Countries information or specific country information ? Say All Countries or say a specific Resion Fox example... (India)'
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    # mytestSession = {"Product": Product_name}
    
    mytestSession = {'packdatacheck': {'product': Product_name} ,'Product':Product_name}
    print mytestSession
    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mytestSession)


def getOnlyCountryData(event):
    print "HEYYYY I am in getOnlyCountryData"
    if 'resolutions' in event['request']['intent']['slots']['countries'] and event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['status'][
        'code'] == 'ER_SUCCESS_MATCH':
        country_name = \
        event['request']['intent']['slots']['countries']['resolutions']['resolutionsPerAuthority'][0]['values'][0][
            'value']['name']
    else:
        wrongname_MSG = "Sorry as per you requested Country OR resions  OR Prodcut is not availble."
        reprompt_MSG = "Do you want to hear more about countries Product ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong country name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)

    ResponseDataJson = SendCountryDataReq(country_name)
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Product' in mytestSession:
            Product = mytestSession['Product']
            return getProductCountryWiseDetailsPrice(Product, country_name, event)
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    AllProducts = []
    countries = []
    numbercount = 0
    for pack in availabepacks:
        countries.append(pack['country'])
        AllProducts.append(pack['name'])
        numbercount += 1
    mdata = [s.lower() for s in countries]
    product_calculate = [s.lower() for s in AllProducts]
    product_count = set(product_calculate)
    unique_data = set(mdata)
    # mytestSession = {"Country": country_name}
    if event['session']:
        if 'attributes' in event['session']:
            if 'packdatacheck' in event['session']['attributes']:
                event['session']['attributes']['packdatacheck'].update({'country': country_name})
                event['session']['attributes'].update({'Country': country_name})
                mtattribute = event['session']['attributes']
            else:
                event['session']['attributes']= {'Country': country_name}
                event['session']['attributes']['packdatacheck'] = {'Country': country_name}
                mtattribute = event['session']['attributes']
        else:
            event['session']['attributes'] =  {'Country': country_name}
            event['session']['attributes']['packdatacheck'] = {'Country': country_name}
            mtattribute = event['session']['attributes']

    mreponse = 'for ' + str(country_name) + ' ' + str(len(
        product_count)) + " products are availble . DO You want to check for AllProducts information or specific Product information ?"
    reprompt_MSG = "Do you want to hear more about AllProducts OR a particular Product ?"
    card_TEXT = "You've picked " + str(country_name.lower())
    card_TITLE = "You've picked " + str(country_name.lower())
    event['session']['attributes']= {'packdatacheck': {'country': country_name,},'Country': country_name}
    mytestSession = event['session']['attributes']
    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)

""" This is Demo """

def get_PacksData(event,mtattribute):
    if mtattribute:
        print "I am in Get pack data with Strength"
        if event['session']:
            print mtattribute
            event['session']['attributes'] = mtattribute
    else:
        print "I am In get_PacksData "
        strengths = False
        PriceTypes = False
        Product_name = None
        country_name = None

    try:
        if 'value' in event['request']['intent']['slots']['strength'] and event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
            strengths = event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
            
    except Exception as e:
        print e
        strengths = False
        if 'strength' in event['session']['attributes']['packdatacheck']:
            del event['session']['attributes']['packdatacheck']['strength']
        print "strength not Found"
        pass
    try:
        if 'value' in event['request']['intent']['slots']['pricetypes'] and event['request']['intent']['slots']['pricetypes']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
            PriceTypes = event['request']['intent']['slots']['pricetypes']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']

    except Exception as e:
        print e
        PriceTypes = False
        if 'pricetypes' in event['session']['attributes']['packdatacheck']:
            del event['session']['attributes']['packdatacheck']['pricetypes']
        print "pricetypes not Found"
        pass
    if 'attributes' in event['session']:
        if 'packdatacheck' in event['session']['attributes']:
            packdatacheck = event['session']['attributes']['packdatacheck']
            country_name = packdatacheck.get('country', None)
            Product_name = packdatacheck.get('product', None)
            if strengths:
                event['session']['attributes']['packdatacheck'].update({'strength': strengths})
            if PriceTypes:
                event['session']['attributes'].update({'strengthCheck': True})
                event['session']['attributes']['packdatacheck'].update({'pricetypes': PriceTypes})

            try:
                Product_name = urllib2.quote(Product_name)
                url = str(BASEURL) + 'productcountryPriceCheck/' + str(Product_name) + '/' + str(country_name)
                Product_name = urllib2.unquote(Product_name)
                country_name = urllib2.unquote(country_name)
                ResponseData = urllib2.urlopen(url)
            except Exception as e:
                print e
                wrongname_MSG = "Sorry This Pack is not availble as per request."
                reprompt_MSG = "Do you want to hear more about Pack?"
                card_TEXT = "Use the full form."
                card_TITLE = "Wrong Pack."
                return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG,
                                                                  False, False)
            ResponseDataJson = json.loads(ResponseData.read())
            availabepacks = ResponseDataJson['data']['information']['availabepacks']
            # if 'strength' not in event['session']['attributes']['packdatacheck']:
            if 'strengthCheck' not in event['session']['attributes']:
                print "goto Before Strength"
                mtattribute = event['session']['attributes']
                return BeforeStrength(Product_name, country_name, event, availabepacks,mtattribute)
            elif 'pricetypes' not in event['session']['attributes']['packdatacheck']:
                print "goto Before PriceType"
                strength = event['session']['attributes']['packdatacheck']['strength']
                # event['session']['attributes']['packdatacheck']
                return BeforePriceType(Product_name, country_name, event, availabepacks,mtattribute)
            else:
                strength = event['session']['attributes']['packdatacheck']['strength']
                pricetypes = event['session']['attributes']['packdatacheck']['pricetypes']
                return RetuenPrice(Product_name, country_name, event, strength, pricetypes, availabepacks)
        else:
            myreponse = "Sorry I didn't get, Please Choose A Region, country and Product  \n So I Can Find A Pack For You"  # +str(event['session']['attributes'])
            reprompt_MSG = "Wnat Do you want ?"
            card_TEXT = "Choose A Region, country and Product "
            card_TITLE = "Choose A Region, country and Product "
            event['session']['attributes']['packdatacheck'] = False
            mtattribute = event['session']['attributes']
            # mtattribute.update(event['session']['attributes'])
            return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          mtattribute)
    else:
        # myreponse = "I didn't understand the Product   Please repeate once"  # +str(event['session']['attributes'])
        myreponse = "I don't have that much information Please go through another country or  Product "  # +str(event['session']['attributes'])
        reprompt_MSG = "Wnat Do you want ?"
        card_TEXT = "Choose A Region, country and Product "
        card_TITLE = "Choose A Region, country and Product "
        # mtattribute = event['session']['attributes']['packdatacheck'] = False
        return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False, False)


def BeforeStrength(Product_name, country_name, event, availabepacks,mtattribute):
    print "I am in BeforeStrength" 
    strengths = False
    try:
        if 'value' in event['request']['intent']['slots']['strength'] and event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
            strengths = event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
            print "Strengths Found",strengths
    except Exception as e:
        print e
        print "strength not Found"
        pass
    # print mtattribute
  
    numbercount = 0
    teststrength = []
    Mysenteces = []
    msgteststrength = []
    for pack in availabepacks:
        numbercount += 1
        teststrength.append(pack['strength'])
        msgteststrength.append(pack['strength']+' '+pack['strengthUnit'])

    mdata = [s.lower() for s in msgteststrength]
    strength_count = set(mdata)
    unique_data = list(strength_count)
    if strengths:
        if strengths in teststrength:
            if 'strengthCheck' in mtattribute:
                print "Before Detetion mtattribute"
                del mtattribute['strengthCheck']
                print "after Detetion mtattribute"
            event['session']['attributes'].update(mtattribute)
            return BeforePriceType(Product_name, country_name, event, availabepacks,mtattribute)
        else:
            mymsg = ', '.join(map(str, unique_data))
            if len(unique_data) > 1 and str(strengths) not in  ["all","all strengths"]:
                myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Strength is Not available, Avalible Strengths are  as Follows : "+str(mymsg) +" Please Choose One from thease or say all Strengths so I will Provide You the price types for the Strength "
            else:
                myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Avalible Strength as follows : "+str(mymsg)+ "  Please Choose the Strength or say All Strengths so I will Provide You the price types for the Strength "
            mtattribute.update({'strengthCheck':True})
    elif len(unique_data) == 0:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Strengths are Not available"
    elif len(unique_data) == 1:
        mdata = [s.lower() for s in msgteststrength]
        strength_count = set(mdata)
        unique_data = list(strength_count)
        mymsg = ', '.join(map(str, unique_data))
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + str(mymsg) + " strength  is availble,  Do you Want to know the availble price types for this Strength then say, " + str(mymsg) 
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' '  + str(len(unique_data)) + " Strength  are  available, Do you Want to know all Strength Or Specific Strength Wise Products"
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    
    # print mtattribute
    # event['session']['attributes'] = mtattribute.update('strengthCheck':True)
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)
def DetailsStrength(Product_name, country_name, event, availabepacks,mtattribute):
    print "I am in DetailsStrength" 
    numbercount = 0
    teststrength = []
    Mysenteces = []
    for pack in availabepacks:
        numbercount += 1
        teststrength.append(pack['strength']+' '+pack['strengthUnit'])
    mdata = [s.lower() for s in teststrength]
    strength_count = set(mdata)
    unique_data = list(strength_count)
    mymsg = ', '.join(map(str, unique_data))
    if len(unique_data) == 0:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Strengths are Not available" + " DO You want to check More information So Say Any Product Name and Country name"
    if len(unique_data)==1:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + str(mymsg) + " strength  is availble,  Do you Want to know the availble price types for this Strength then say, " + str(mymsg) 
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + "  following strength  are availble " + str(mymsg) + " Do you Want to know the price type for all Strength Or for a Specific Strength "
    reprompt_MSG = "Do you want to hear more about a particular strength or all strengths?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    event['session']['attributes']['packdatacheck'].update({'strengthForAllCheck':True })
    mtattribute = event['session']['attributes']
    # print event['session']['attributes']['packdatacheck']
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)


def BeforePriceType(Product_name, country_name, event, availabepacks,mtattribute):
    print "I am in BeforePriceType" 
    numbercount = 0
    testprice_type = []
    Mysenteces = []
    strengths = False
    if 'strengthForAllCheck' not in event['session']['attributes']['packdatacheck']:
        try:
            if 'value' in event['request']['intent']['slots']['strength'] and event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
                strengths = event['request']['intent']['slots']['strength']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
                if not strengths or strengths is None:
                    strengths = event['session']['attributes']['packdatacheck']['strength']
                if str(strengths) == 'all Strength' or str(strengths) == "all":
                    return DetailsStrength(Product_name, country_name, event, availabepacks,mtattribute)
        except Exception as e:
            print e
            myreponse = "I didn't understand the Strength Please repeate it once"  # +str(event['session']['attributes'])
            reprompt_MSG = "Wnat Do you want ?"
            card_TEXT = "Medicine Strength"
            card_TITLE = "Medicine Strength"
            return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False, False)
    strengths = event['session']['attributes']['packdatacheck']['strength']
    # strengths = event['session']['attributes']['packdatacheck']['strength']
    for pack in availabepacks:
        numbercount += 1
        if str(strengths) == str(pack['strength'])  or str(strengths) == 'all Strength'or str(strengths) == "all":
            testprice_type.append(pack['price_type'])
    mdata = [s.lower() for s in testprice_type]
    strength_count = set(mdata)
    unique_data = list(strength_count)
    # mymsg = ', '.join(map(str, Mysenteces))
    if len(unique_data) == 0 or unique_data == []:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Packs are Not available " + " DO You want to check More information So Say Any Product Name and Country name"
    elif len(unique_data) == 1:
        PriceTypes = unique_data[0]
        # print PriceTypes
        return RetuenPrice(Product_name, country_name, event, strengths, PriceTypes, availabepacks)
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' '  +str(len(unique_data))+ " Price Types are  available  , Do you Want to know the Prouct Details for  all PriceTypes Or Specific PriceType "
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    mtattribute = event['session']['attributes']
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)


def DetailsPrice(Product_name, country_name, event, availabepacks,mtattribute):
    print " I am in DetailsPrice"
    numbercount = 0
    testprice_type = []
    Mysenteces = []
    if 'strength' in event['session']['attributes']['packdatacheck']:
        strength = event['session']['attributes']['packdatacheck']['strength']
    else:
        strength = False
    for pack in availabepacks:
        # print pack['strength'],strength
        if str(strength).lower() ==str(pack['strength']).lower() or str(strength).lower() == 'all Strength'.lower() or str(strength).lower() == "all".lower():
            testprice_type.append(pack['price_type'])
            numbercount += 1

    mdata = [s.lower() for s in testprice_type]
    strength_count = set(mdata)
    unique_data = list(strength_count)
    # print unique_data
    mymsg = ', '.join(map(str, unique_data))
    if len(unique_data) == 0 or unique_data == []:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Packs are Not available " + " DO You want to check More information So Say Any Product Name and Country name"
    if len(unique_data) == 1:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + "  following price type availble " + str(mymsg) + " Do you Want to know the Product Details for this price type then say ,"+str(mymsg) 
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + "  following price types  are availble " + str(mymsg) + " Do you Want to know the Product Details for all price type Or for a Specific price type "
    reprompt_MSG = "Do you want to hear more about a particular price type or price types?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())  
    event['session']['attributes']['packdatacheck'].update({'PriceForAllCheck':True })
    mtattribute = event['session']['attributes']
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)
def RetuenPrice(Product_name, country_name, event, strengths, PriceTypes, availabepacks):
    print "I am in RetuenPrice" 
    print PriceTypes
    if 'PriceForAllCheck' not in (event['session']['attributes']['packdatacheck']):
        try:
            if 'value' in event['request']['intent']['slots']['pricetypes'] and event['request']['intent']['slots']['pricetypes']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
                PriceTypes = event['request']['intent']['slots']['pricetypes']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
                if str(PriceTypes) == 'all PriceTypes' or str(PriceTypes) == "all":
                    mtattribute = event['session']['attributes']['packdatacheck'].update({'pricetypes': PriceTypes})
                    return DetailsPrice(Product_name, country_name, event, availabepacks,mtattribute)
        except Exception as e:
            print e
            print "Price Type Not Found"
            pass
    numbercount = 0
    Mysenteces = [] 
    for pack in availabepacks:
        numbercount +=1
        if strengths or PriceTypes:
            # print " I am In 1 ",pack['price_type'],PriceTypes
            if str(pack['strength']).lower() == str(strengths).lower() and str(pack['price_type']).lower() == str(PriceTypes).lower():
                # print " I am In 1 ",pack['price_type']
                test = str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
                Mysenteces.append(test)
            if str(strengths).lower() == "all Strength".lower() or str(strengths).lower() == "all".lower() and str(PriceTypes).lower() == "all PriceTypes".lower() or str(PriceTypes).lower() == "all".lower():
                # print " I am In 2 ",pack['price_type']
                test = str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
                Mysenteces.append(test)
            if str(strengths).lower() == "all Strength".lower() or str(strengths).lower() == "all".lower() and str(pack['price_type']).lower() == str(PriceTypes).lower():
                # print " I am In 3 ",pack['price_type']
                test = str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
                Mysenteces.append(test)
            if str(PriceTypes).lower() == "all PriceTypes".lower() or str(PriceTypes).lower() == "all".lower() and str(pack['strength']).lower() == str(strengths).lower():
                # print " I am In 4 ",pack['price_type']
                test = str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
                Mysenteces.append(test)
        else:
            test = str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
            Mysenteces.append(test)

    mdata = [s.lower() for s in Mysenteces]
    mdata_count = set(mdata)
    mdata_unique_data = list(mdata_count)
    n = 1
    result = []
    for mytestdata in mdata_unique_data:
        result.append(str(n) +' : '+str(mytestdata))
        n +=1
    print len(result)
    mymsg = ', '.join(map(str, result))
    if n == 1 :
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " Packs are Not available" + " DO You want to check More information So Say Any Product Name and Country name"
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + ' ' + str(len(mdata_unique_data)) + " Packs are available in as follows  :" + str(mymsg) + " ...., Do You want to check More information So Say Any Product Name and Country name"  # +str(event['session']['attributes'])
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    event['session']['attributes'] = {'allClear':True}
    mytestSession = event['session']['attributes'] 
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,mytestSession)

""" END  Demo """


def getProductCountryWiseDetailsPrice(Product_name, country_name, event):
    print "Hello I am in  getProductCountryWiseDetailsPrice"
    try:
        Product_name = urllib2.quote(Product_name)
        country_name = urllib2.quote(country_name)
        url = str(BASEURL) + 'productcountryPriceCheck/' + str(Product_name) + '/' + str(country_name)
        ResponseData = urllib2.urlopen(url)
        Product_name = urllib2.unquote(Product_name)
        country_name = urllib2.unquote(country_name)
    except Exception as e:
        print e
        return SendAvailableProductInCountry(Product_name)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 0
    packcount = 0
    Mysenteces = []
    Mystrength_list = []
    Myprice_type_list = []
    for pack in availabepacks:
        if len(availabepacks) > 1:
            packcount += 1
            Myprice_type_list.append(pack['price_type'])
            Mystrength_list.append(str(pack['strength']) + ' ' + str(pack['strengthUnit']))
        else:
            numbercount += 1
            test = '' + str(numbercount) + '. ' + str(pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
            Mysenteces.append(test)

    Mystrength_list_lower = [s.lower() for s in Mystrength_list]
    Mystrength_list_unnique = set(Mystrength_list_lower)
    Mystrength_list_commaSeprated = ', '.join(map(str, list(Mystrength_list_unnique)))

    Myprice_type_list_lower = [s.lower() for s in Myprice_type_list]
    Myprice_type_list_unnique = set(Myprice_type_list_lower)
    # print Myprice_type_list_unnique
    Myprice_type_list_commaSeprated = ', '.join(map(str, list(Myprice_type_list_unnique)))

    checkPrice = ', '.join(map(str, Mysenteces))
    if packcount > 1:
        strgnthandpricetype = None
        if len(list(Myprice_type_list_unnique)) > 0 and len(list(Mystrength_list_unnique)) > 0:
            if len(list(Mystrength_list_unnique)) == 1:
                strgnthandpricetype = str(Mystrength_list_commaSeprated)+" strengths is available Do you Want to know the availble price types for this Strength then say, " + str(Mystrength_list_commaSeprated) 
            else:
                strgnthandpricetype = str(len(list(Mystrength_list_unnique)))+" strengths are available Do You want to check all strengths or a specific strength"# + +''# + ' and Avalible PriceTypes = ' + Myprice_type_list_commaSeprated
        # else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " " + str(strgnthandpricetype) #+ " Packs are availble !\n Do You want to check all packs or check for a specific pack ?"# \n Say all Packs , Say strength Of Medicine For example 100 MG \n or Say Price Type So I Can Give you a Filtred Result" + str(strgnthandpricetype)
        # reprompt_MSG = "Do You want to chek all packs or check a specific pack ? For all packs say Allpacks and For a specific pack give me a pack name or strength of pack so I can tell you the available specific packs."
        reprompt_MSG = "Do You want to check all strengths or a specific strength"
        mtattribute = {'packdatacheck': {'country': country_name, 'product': Product_name},'Product': Product_name, 'Country': country_name}
    else:
        myreponse = "for " + str(Product_name) + " in " + str(country_name) + " is available in following pack :" + str(checkPrice) + " DO You want to check More information So Say Any Product Name and Country name"  # +str(event['session']['attributes'])
        mtattribute = {'Product': False, 'Country': False}
        reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    if 'attributes' in event['session']:
        # if 'packdatacheck' in event['session']['attributes']:
            # event['session']['attributes'].update(mtattribute)
        event['session']['attributes'].update(mtattribute)
        mtattribute = event['session']['attributes']
    # else:
        # event['session']['attributes']= {'packdatacheck': {'country': country_name, 'product': Product_name},'Country': country_name,'Product':Product_name}
        # mtattribute = event['session']['attributes']
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)


def getProductResionWiseDetailsPrice(Product_name, region_name, event):
    print "I am In getProductResionWiseDetailsPrice"
    try:
        Product_name = urllib2.quote(Product_name)
        url = str(BASEURL) + 'productregionPriceCheck/' + str(Product_name) + '/' + str(region_name)
        ResponseData = urllib2.urlopen(url)
        Product_name = urllib2.unquote(Product_name)
        region_name = urllib2.unquote(region_name)

    except Exception as e:
        print e
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 0
    packcount = 0
    country_data = []
    Mysenteces = []
    for pack in availabepacks:
        if len(availabepacks) > 1:
            packcount += 1
            country_data.append(pack['country'])

        else:
            test = '' + str(numbercount) + '. ' + str(pack['description']) + ' Price For ' + str(
                pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
            Mysenteces.append(test)
            numbercount += 1
    mdata = [s.lower() for s in country_data]
    unique_data = set(mdata)

    mtattribute = {}
    # checkPrice = ', '.join(map(str, Mysenteces))
    if packcount > 1:
        myreponse = "for " + str(Product_name) + " in " + str(
            region_name) + " are availble in  " + str(len(unique_data)) + ' Countries with ' + str(
            packcount) + " Packs! \n Do You want to chek all Countries data Or specific Country Data "  # +str(event['session']['attributes'])
        reprompt_MSG = "Do You want to chek for all Countries or check  for a specific Countries ? For all Countries say AllCountries and For a specific Countries give me a Country name "
        if 'packdatacheck' in event['session']['attributes']:
            event['session']['attributes']['packdatacheck'].update({'region':region_name})
            mtattribute = event['session']['attributes']
    else:
        myreponse = "for " + str(Product_name) + " in " + str(region_name) + " is available in following pack :" + str(checkPrice + " DO You want to check More information So Say Any Product Name and Country name")  # +str(event['session']['attributes'])
        mtattribute = {'Product': False, 'region': False}
        mtattribute.update(event['session']['attributes'])
        reprompt_MSG = "Do you want to hear more about a particular Country?"
    card_TEXT = "You've picked " + str(Product_name.lower())
    card_TITLE = "You've picked " + str(Product_name.lower())
    mtattribute = event['session']['attributes']
    return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mtattribute)


def GetAllProductInformationWithinCountry(event):
    print "I AM IN GetAllProductInformationWithinCountry"
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Product' in mytestSession:
            Product_name = mytestSession['Product']
            try:
                Product_name = urllib2.quote(Product_name)
                url = str(BASEURL) + 'productlistcheck/' + str(Product_name)
                ResponseData = urllib2.urlopen(url)
                Product_name = urllib2.unquote(Product_name)
            except Exception as e:
                print e
                wrongname_MSG = "Sorry This product is not availble as per request."
                reprompt_MSG = "Do you want to hear more about a particular Product?"
                card_TEXT = "Use the full form."
                card_TITLE = "Wrong Product."
                return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
                # return SendAvailableProductInCountry(Product_name)
            ResponseDataJson = json.loads(ResponseData.read())
            availabepacks = ResponseDataJson['data']['information']['availabepacks']
            numbercount = 0
            Mysenteces = []
            countries = []
            for pack in availabepacks:
                numbercount += 1
                test = ' ' + str(numbercount) + '. ' + str(pack['description']) + ' Price For ' + str(
                    pack['price_type']) + ' is ' + str(pack['price']) + ' ' + str(pack['currency'])
                Mysenteces.append(test)
                countries.append(pack['country'])
            checkPrice = ', '.join(map(str, Mysenteces))
            mdata = [s.lower() for s in countries]
            unique_data = set(mdata)
            countries = list(unique_data)
            contriesstring = ', '.join(map(str, countries))
            mreponse = 'for ' + str(numbercount) + ' packs of ' + str(
                Product_name) + " are availble in " + str(contriesstring)
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "You've picked " + str(Product_name.lower())
            card_TITLE = "You've picked " + str(Product_name.lower())
            return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                              mytestSession)
        elif 'Region' in mytestSession:
            region_name = mytestSession['Region']
            # region_name = event['request']['intent']['slots']['regions']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
            ResponseDataJson = SendResionWiseCountryNameDataReq(region_name)
            if 'attributes' in event['session']:
                mytestSession = event['session']['attributes']
                if 'Product' in mytestSession:
                    Product = mytestSession['Product']
                    return getProductCountryWiseDetailsPrice(Product, region_name, event)
                else:
                    mytestSession["Region"] = region_name
            else:
                mytestSession = {"Region": region_name}
            availabepacks = ResponseDataJson['data']['information']
            countrycount = availabepacks['country']
            Countries = ', '.join(map(str, countrycount))
            availabepacks_count = availabepacks['availabepacks']
            mreponse = 'for ' + str(region_name) + ' following countries availabe ' + str(
                Countries) + ' .DO You want to specific Countries information ?'
            reprompt_MSG = "DO You want to check for a specific Countries information ?"
            card_TEXT = "You've picked " + str(region_name.lower())
            card_TITLE = "You've picked " + str(region_name.lower())
            return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                              mytestSession)
        else:
            wrongname_MSG = "Sorry I didn't Understand Product Name Will You please tell me reapeat Prodcut name."
            reprompt_MSG = "Do you want to hear more about a particular Product?"
            card_TEXT = "Use the full form."
            card_TITLE = "Wrong Product."
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                              False)

    else:
        wrongname_MSG = "Sorry Didn't Find anything Will you please repeat."
        reprompt_MSG = "Do you want to hear more Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)


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
            return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                              False)

        ResponseDataJson = SendCountryDataReq(country_name)
        availabepacks = ResponseDataJson['data']['information']['availabepacks']
        numbercount = 0
        AllProducts = []
        Mysenteces = []
        countries = []
        for pack in availabepacks:
            numbercount += 1
            test = ' ' + str(numbercount) + '. ' + str(pack['name']) + ' : ' + str(
                pack['description']) + ' Price For ' + str(pack['price_type']) + ' is ' + str(
                pack['price']) + ' ' + str(pack['currency'])
            Mysenteces.append(test)
            countries.append(pack['country'])
            AllProducts.append(pack['name'])
        checkPrice = ', '.join(map(str, Mysenteces))
        product_calculate = [s.lower() for s in AllProducts]
        product_count = set(product_calculate)
        product_list = list(product_count)
        product_names = ', '.join(map(str, product_list))
        if numbercount > 1:
            mreponse = 'for ' + str(country_name) + ' ' + str(
                len(product_count)) + " products are availble, and following are the names of product " + str(
                product_names)
        else:
            mreponse = 'for ' + str(country_name) + ' ' + str(
                len(product_count)) + " products are availble following are the Details information of product " + str(
                checkPrice)
        reprompt_MSG = "Do you want to hear more about AllProducts OR a particular Product ?"
        card_TEXT = "You've picked " + str(country_name.lower())
        card_TITLE = "You've picked " + str(country_name.lower())
        mytestSession = {'Country': country_name}
        return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          mytestSession)
    else:
        wrongname_MSG = "Sorry Didn't Find anything Will you please repeat."
        reprompt_MSG = "Do you want to hear more Product?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)

def getOnlyRegionsData(event):
    print " i am ain getOnlyRegionsData"
    if 'resolutions' in event['request']['intent']['slots']['regions'] and event['request']['intent']['slots']['regions']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_MATCH':
        region_name = event['request']['intent']['slots']['regions']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    else:
        myreponse = "I didn't understand, Will You Please repeate once"  # +str(event['session']['attributes'])
        reprompt_MSG = "Wnat Do you want ?"
        card_TEXT = "Medicine Strength"
        card_TITLE = "Medicine Strength"
        return output_json_builder_with_reprompt_and_card(myreponse, card_TEXT, card_TITLE, reprompt_MSG, False, False)


    ResponseDataJson = SendResionDataReq(region_name)
    if 'attributes' in event['session']:
        mytestSession = event['session']['attributes']
        if 'Product' in mytestSession:
            Product = mytestSession['Product']
            return getProductResionWiseDetailsPrice(Product, region_name, event)
        else:
            # mytestSession["Region"] = region_name
            mytestSession = event['session']['attributes'].update({'Region':region_name})

    else:
        mytestSession = {'packdatacheck': {'region': region_name},'Region':region_name}
        # mytestSession = {}
        # mytestSession["Region"] = region_name
        # event['session']['attributes'] = mytestSession

    availabepacks = ResponseDataJson['data']['information']
    countrycount = availabepacks['countrycount']
    availabepacks_count = availabepacks['availabepacks']
    mreponse = 'for ' + str(region_name) + '  ' + str(
        availabepacks_count) + ' Packs are availble in ' + str(
        countrycount) + " countries. DO You want to check for All Countries information or specific Countries information ?"
    reprompt_MSG = "Do You want to check for All Countries information or specific Countries information ?"
    card_TEXT = "You've picked " + str(region_name.lower())
    card_TITLE = "You've picked " + str(region_name.lower())

    return output_json_builder_with_reprompt_and_card(mreponse, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                      mytestSession)



def SendCountryDataReq(country_name):
    try:
        country_name = urllib2.quote(country_name)
        url = str(BASEURL) + 'countrywiseproductcheck/' + str(country_name)
        print url
        ResponseData = urllib2.urlopen(url)
        country_name = urllib2.unquote(country_name)
    except Exception as e:
        print e
        wrongname_MSG = "Sorry This country is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular country?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong country name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    return ResponseDataJson


def SendResionDataReq(region_name):
    try:
        region_name = urllib2.quote(region_name)
        url = str(BASEURL) + 'regionwisecountrycheck/' + str(region_name)
        print url
        ResponseData = urllib2.urlopen(url)
        region_name = urllib2.unquote(region_name)
    except Exception as e:
        print e
        wrongname_MSG = "Sorry This Region is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Resion?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Resion name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    return ResponseDataJson

def SendAvailableProductInCountry(Product_name):
    try:
        Product_name = urllib2.quote(Product_name)
        url = str(BASEURL) + 'productlistcheck/' + str(Product_name)
        print url
        ResponseData = urllib2.urlopen(str(url))
        Product_name = urllib2.unquote(Product_name)

    except Exception as e:
        print e
        wrongname_MSG = "Sorry This product is not availble as per request."
        reprompt_MSG = "Do you want to hear about more Products ?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Product."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,False)
    ResponseDataJson = json.loads(ResponseData.read())
    availabepacks = ResponseDataJson['data']['information']['availabepacks']
    numbercount = 0
    countries = []
    for pack in availabepacks:
        countries.append(pack['country'])
    mdata = [s.lower() for s in countries]
    unique_data = set(mdata)
    countries = list(unique_data)
    checkPrice = ', '.join(map(str, countries))

    wrongname_MSG = "Sorry This product is not availble as per requested Country, product is availble in following Countries : "+str(checkPrice)
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "Use the full form."
    card_TITLE = "Wrong Product."
    mytestSession = {'packdatacheck': {'product': Product_name} ,'Product':Product_name}

    return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG,
                                                              False, mytestSession)


def SendResionWiseCountryNameDataReq(region_name):
    try:
        region_name = urllib2.quote(region_name)
        url = str(BASEURL) + 'regionwisecountryname/' + str(region_name)
        print url
        ResponseData = urllib2.urlopen(url)
        region_name = urllib2.unquote(region_name)
    except Exception as e:
        print e
        wrongname_MSG = "Sorry This Region is not availble as per request."
        reprompt_MSG = "Do you want to hear more about a particular Resion?"
        card_TEXT = "Use the full form."
        card_TITLE = "Wrong Resion name."
        return output_json_builder_with_reprompt_and_card(wrongname_MSG, card_TEXT, card_TITLE, reprompt_MSG, False,
                                                          False)
    ResponseDataJson = json.loads(ResponseData.read())
    return ResponseDataJson


def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True, False)


def assistance(event):
    assistance_MSG = "Please give me a product name and contry name so I can give you a proper information regarding Product"
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, False)


def yes_continue_the_skill(event):
    yesIntetnt_MSG = "Ok, Please Continue with your query"
    reprompt_MSG = ""
    card_TEXT = "Yes Intent."
    card_TITLE = "Yes Intent"
    return output_json_builder_with_reprompt_and_card(yesIntetnt_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, False)


def fallback_call(event):
    fallback_MSG = "Sorry I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a particular Product?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False, False)


def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    mmtest_dict = {}
    mmtest_dict['type'] = "SSML"
    # mmtest_dict['ssml'] = '<speak><amazon:effect name="whispered">'+str(repr_text)+'.</amazon:effect>.</speak>'
    # mmtest_dict['text'] = str(repr_text)+'<break time="500ms"/>'
    mmtest_dict['ssml'] = '<speak><amazon:effect name="whispered">This is Reprompt reply.</amazon:effect><break time="5s"/>'+str(repr_text)+'</speak>'
    #  {
    #     "type": "SSML",
    #     "ssml": "<speak>"+str(repr_text)+"This output speech uses SSML.</speak><break time="500ms"/>"
    # }

    # "type": "SSML"/
    # "ssml":'<speak> <break time="3s"/> '+str(repr_text)+'</speak>'
    # reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    reprompt_dict['outputSpeech'] = mmtest_dict
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


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value,
                                               mytestSession):
    response_dict = {}
    response_dict['version'] = '1.0'
    if mytestSession:
        print mytestSession
        response_dict['sessionAttributes'] = mytestSession
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title,
                                                                              reprompt_text, value)
    return response_dict

# if __name__== "__main__":
