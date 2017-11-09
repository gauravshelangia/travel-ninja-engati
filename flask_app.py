
# A very simple Flask Hello World app for you to get started with...
import requests
import json
import utility
import train_code
import datetime as dt
from random import randint
from flask import Flask,session,request, flash, url_for, redirect, render_template, abort ,g,make_response, jsonify, send_from_directory

app = Flask(__name__, template_folder='templates')
apikey = 'a6f5i1ae2f'
api_key = 'AIzaSyC6LyOf4jS9zACpy587zOF1Yyw80Uz58Dw' #vivek iiit key
transit_modes=['bus','train']
base_url_bus="https://maps.googleapis.com/maps/api/directions/json?&mode=transit&transit_mode={transit_mode}&alternatives=true&origin={origin}&destination={destination}&departure_time={departure_time}&key={apikey}"
base_url_hotels="https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}+india+hotel+accommodation+hospitality&key={apikey}"
base_url_restaurant="https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}+india+restaurant+eating place+eatery+food&key={apikey}"
base_url_ATM="https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}+india+ATM&key={apikey}"
base_url_place_details="https://maps.googleapis.com/maps/api/place/details/json?placeid={placeid}&key={apikey}"
base_url_place_photo="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photoreference}&key={apikey}"
g_api_key = '2c941e1ecaf4b01e124e27f5ca15ac4b'
app_id='e62b6a84'
flight_image='http://images.all-free-download.com/images/graphicthumb/aircraft_in_flight_picture_7_168555.jpg'

city_names_codes={"New Delhi":"DEL","delhi":"DEL","mumbai":"BOM","Bombay":"BOM","Bengaluru":"BLR","bangalore":"BLR",
"chennai":"MAA","madras":"MAA","kolkata":"CCU","calcutta":"CCU","cochin":"COK","ahmedabad":"AMD",
"hyderabad":"HYD","pune":"PNQ","dabolim":"GOI","trivandrum":"TRV","thiruventpuram":"TRV","lucknow":"LKO",
"jaipur":"JAI","guwahati":"GAU","kozikhode":"CCJ","srinagar":"SXR","bhubneshwar":"BBI","vishakapatnam":"VTZ",
"coimbatore":"CJB","indore":"IDR","mangalore":"IXE","nagpur":"NAG","patna":"PAT","chandigarh":"IXC",
"tiruchilapalli":"TRZ","varanasi":"VNS","raipur":"RPR","amritsar":"ATQ","jammu":"IXJ",
"bagdogra":"IXB","siliguri":"IXB","vadodra":"BDQ","Badora":"BDQ","agartala":"IXA","portblair":"IXZ",
"madurai":"IXM","imphal":"IMF","ranchi":"IXR","udaipur":"UDR","dehradun":"DED","bhopal":"BHO","leh":"IXL",
"rajkot":"RAJ","vijaywada":"VJA","tirupati":"TIR","dibrugarh":"DIB","jodhpur":"JDH","aurangabad":"IXU",
"rajahmundry":"RJA","silchar":"IXS","jabalpur":"JLR","aizwal":"AJL"}

counter_map = {"Domestic":"100","domestic":"100","International":"0","international":"0"}
f_class={"Business":"B","buiseness":"B","Economy":"E", "economy":"E"}
infants=0
children=0
adults=1

flight_url="""http://developer.goibibo.com/api/search/?app_id={app_id}&app_key={api_key}&format=json&source={source}&destination={destination}&dateofdeparture={dep_date}&dateofarrival={arr_date}&seatingclass={fclass}&adults={adults}&children={children}&infants={infants}&counter={counter}"""

quiz_json = utility.new_quiz_json()
stn_code = train_code.train_code()

@app.route('/google_map',methods=['GET'])
def google_map():
    if request.method == 'GET':
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        return render_template('user_location_googlemap.html')

@app.route('/flight/<source>/<destination>/<dep_date>')
def find_flights(source,destination,dep_date,arr_date="",fclass="economy",
    adults=1,children=0,infants=0,counter="Domestic"):
    source=source.lower()
    destination=destination.lower()
    a_source = city_names_codes.get(source)
    a_destination = city_names_codes.get(destination)
    if len(source)==0 or len(destination)==0:
        return "Source or destination city not matched to the codes"

    flight_search_url = flight_url.format(app_id=app_id,api_key=g_api_key,source=a_source,
    destination=a_destination,dep_date=dep_date,arr_date=arr_date,fclass=f_class.get(fclass),
    adults=adults,children=children,infants=infants,counter=counter_map.get(counter))

    flights={}
    jaane_ki_flights=[]
    aane_ki_flights=[]

    r = requests.get(flight_search_url)
    resp = r.json()

    data_length = resp['data_length']
    if data_length>1:
        aane_ki_flights = resp['data']['returnflights']
        jaane_ki_flights = resp['data']['onwardflights']
    else:
        flights['jaane_ki_flights'] = jaane_ki_flights
        flights['aane_ki_flights'] = aane_ki_flights
        msg="Flight not found"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
        return json.dumps(result)

    jaane_ki_flights = sorted(jaane_ki_flights, key= lambda k: int(k['fare']['totalfare']))
    aane_ki_flights = sorted(aane_ki_flights, key= lambda k: int(k['fare']['totalfare']))
    if len(jaane_ki_flights)>10:
        jaane_ki_flights=jaane_ki_flights[:10]
    if len(aane_ki_flights)>10:
        aane_ki_flights=aane_ki_flights[:10]        

    flights['jaane_ki_flights'] = jaane_ki_flights
    flights['aane_ki_flights'] = aane_ki_flights
    templates=[]
    # print(json.dumps(flights,indent=4))
    for flight in flights['jaane_ki_flights']:
        temp={
        "title": "{}({})\n Class:{} \n {}({}) -{}({})\nDuration: {}".format(flight["airline"],flight["flightno"],flight["seatingclass"],source,flight["arrtime"],destination,flight["deptime"],flight["duration"]),
        "subtitle": "Total Price: {}\nStop: {}\n{}".format(flight["fare"]["totalfare"],flight["stops"],flight["warnings"]),
        "image_url":flight_image
        }
        templates.append(temp)

    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)


bus_url = """https://developer.goibibo.com/api/bus/search/?app_id={app_id}&app_key={api_key}&format=json&source={source}&destination={destination}&dateofdeparture={dep_date}&dateofarrival={arr_date}"""

@app.route('/bus/<source>/<destination>/<dep_date>')
def find_bus(source,destination,dep_date,arr_date=""):
    source=source.lower()
    destination=destination.lower()
    bus_search_url=bus_url.format(app_id=app_id,api_key=g_api_key,source=source,
    destination=destination,dep_date=dep_date,arr_date=arr_date)
    #print(bus_search_url)
    buses={}
    jaane_ki_buses=[]
    aane_ki_buses=[]
    try:
        response = requests.get(bus_search_url)
        response = response.json()
        aane_ki_buses = response['data']['returnflights']
        jaane_ki_buses = response['data']['onwardflights']

        try :
            jaane_ki_buses = sorted(jaane_ki_buses, key= lambda k: int(k['fare']['totalfare']))
            if len(jaane_ki_buses)>10:
                jaane_ki_buses=jaane_ki_buses[:10]
            elif len(jaane_ki_buses)==0:
                msg="No Bus found. Try some other route"
                result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
                return json.dumps(result)
                    
        except KeyError:
            msg="Bus not found"
            result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
            return json.dumps(result)

        try:
            aane_ki_buses = sorted(aane_ki_buses, key= lambda k: int(k['fare']['totalfare']))
            if len(aane_ki_buses)>10:
                aane_ki_buses=aane_ki_buses[:10]
        except KeyError:
            print ("empty buses aane ki buses")

        buses['jaane_ki_buses'] = jaane_ki_buses
        buses['aane_ki_buses'] = aane_ki_buses
        templates=[]
        # print(json.dumps(flights,indent=4))
        for bus in buses['jaane_ki_buses']:
            phone_number = bus['BPPrims']['list'][0]['BPContactNumber']
            phone_numbers = phone_number.split(sep=',')
            phone_number= phone_number[0]
            print(phone_number)
            temp={
            "title": "{}({})\nDuration: {}".format(bus["TravelsName"],bus["BusType"],bus["duration"]),
            "subtitle": "Total Price: {}\n {}({}) -{}({})\n Rating: {}".format(bus["fare"]["totalfare"],bus["origin"],bus["ArrivalTime"],bus["destination"],bus["DepartureTime"],bus["rating"]),
            "image_url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeHBNxXAPZf3jpn7C7gxmAqhl_5u7wii0DPd_qAsT5ITXIEHjp",
            "buttons": [
            {
            "payload": phone_number,
            "title": "\U0001F4DE Call",
            "type": "phone_number"
            }
            ]
            }
            templates.append(temp)

        result = {
        "data": {
        "type": "carousel",
        "templates": templates
        }
        }
        return json.dumps(result)
    except:
        buses['jaane_ki_buses'] = jaane_ki_buses
        buses['aane_ki_buses'] = aane_ki_buses
        msg="Bus not found"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
        return json.dumps(result)

    return result

@app.route('/tourist_place/<place>')
def get_topinsights(place):
    place=place.lower()
    topinsight_url = """https://maps.googleapis.com/maps/api/place/textsearch/json?query=topsights in {place}&key={apikey}"""
    topinsight_search_url = topinsight_url.format(place=place,apikey=api_key)
    topinsights = []
    topinsights_sorted=[]
    response = requests.get(topinsight_search_url)
    print(topinsight_search_url)
    print("RESPONSE")
    print(response)
    response = response.json()
    if response['status'] == "OK":
        results = response['results']
        for result in results:
            topinsight = {}
            try:
                topinsight['name'] = result['name']
                topinsight['address'] = result['formatted_address']
                topinsight['lat'] = result['geometry']['location']['lat']
                topinsight['lng'] = result['geometry']['location']['lng']

                get_place_detail_url = base_url_place_details.format(placeid=result['place_id'],apikey=api_key)
                response_place_detail = requests.get(get_place_detail_url)
                response_place_detail = response_place_detail.json()
                #print(response_place_detail)
                if(response_place_detail['status']=="OK"):
                    photoreference = response_place_detail['result']['photos'][0]['photo_reference']
                    topinsight['image']=base_url_place_photo.format(photoreference=photoreference,apikey=api_key)

                if 'rating' in result:
                    topinsight['rating'] = result['rating']
                else:
                    topinsight['rating'] = '0'
                topinsights.append(topinsight)
            except KeyError:
                topinsight['rating'] = '0'
                topinsights.append(topinsight)
                continue
    else:
        msg="Something went wrong! Please Try Again Later"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
        return json.dumps(result)

    topinsights_sorted = sorted(topinsights, key=lambda x : float(x['rating']),reverse=True)
    templates=[]
    for item in topinsights_sorted:
        image="https://www.bluelankatours.com/wp-content/uploads/2017/01/Sri_Lanka_Public_Holidays_2017.jpg"
        if 'image' in item:
            image=item['image']
        temp={
        "title": "Name: {}\n Rating: {} ".format(item['name'],item  ['rating']),
        "subtitle": "Address: {}".format(item['address']),
        "image_url":image,
        "buttons": [
            {
            "payload": "https://travel-ninja-engati.herokuapp.com/google_map?lat={}&lng={}".format(item['lat'],item['lng']),
            "title": "Find Directions",
            "type": "web_url"
            }
            ]
        }
        templates.append(temp)
    if len(templates)>10:
        templates=templates[:10]
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/')
def hello_world():
    return 'VIVEK PRO HACKER'


@app.route('/live_train/<train_num>/<date>')
def live_train_status(train_num,date):
    r = requests.get('http://api.railwayapi.com/v2/live/train/{}/date/{}/apikey/{}/'.format(train_num,date,apikey))
    resp = r.json()
    if resp["response_code"]==200:
        title="{}({})".format(resp["train"]["name"],resp["train"]["number"])
        templates = []
        temp={
            "title": title,
            "image_url":"http://srv5.indiarailinfo.com/kjfdsuiemjvcya/0/1978394/0/img60454972968.jpg",
            "subtitle": resp["position"],
            "buttons": [
            {
            "payload": "flow_C8CA58B61AA0419090AD75EBEA77289F",
            "title": "Train Route",
            "type": "postback"
            },
            {
            "payload": "flow_690DBB7EF321481E8110082BD44FBF73",
            "title": "Seat Availability",
            "type": "postback"
            }
            ]}
        templates.append(temp)

    else:
        msg="Something went Wrong... Please try again later"
        return json.dumps(msg)
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/pnr_status/<pnr>')
def pnr_status(pnr):
    r = requests.get('http://api.railwayapi.com/v2/pnr-status/pnr/{}/apikey/{}/'.format(pnr,apikey))
    resp = r.json()
    if resp["response_code"]==200:
        title="{}({})\n current status: {}\n  booking status: {}".format(resp["train"]["name"],resp["train"]["number"],resp['passengers'][0]['current_status'],resp['passengers'][0]['booking_status'])
        templates = []
        temp={
            "title": title,
            "image_url":"http://srv5.indiarailinfo.com/kjfdsuiemjvcya/0/1978394/0/img60454972968.jpg",
            "subtitle": "doj : {}\nclass :{}".format(resp['doj'],resp['class']),
            "buttons": [
            {
            "payload": "flow_C8CA58B61AA0419090AD75EBEA77289F",
            "title": "Train Route",
            "type": "postback"
            },
            {
            "payload": "flow_690DBB7EF321481E8110082BD44FBF73",
            "title": "Seat Availability",
            "type": "postback"
            }
            ]}
        templates.append(temp)

    else:
        msg="Something went Wrong... Please try again later"
        return json.dumps(msg)
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/train_route/<train_num>')
def train_route(train_num):
    r = requests.get('http://api.railwayapi.com/v2/route/train/{}/apikey/{}/'.format(train_num,apikey))
    resp = r.json()
    if resp['response_code'] == 200 :
        msg = ""
        for train in resp['route']:
            msg = "{}\n{}({})".format(msg,train['fullname'],train['scharr'])
    else:
        msg=" Route not found. Try again later"
    result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
    return json.dumps(result)

@app.route('/train_btw_stn/<src>/<dst>/<date>')
def train_btw_stn(src,dst,date):
    if src in stn_code and dst in stn_code:
        src=stn_code[src]
        dst=stn_code[dst]
        r = requests.get('http://api.railwayapi.com/v2/between/source/{}/dest/{}/date/{}/apikey/{}/'.format(src,dst,date,apikey))
        resp = r.json()
        if resp['response_code'] == 200 :
            if len(resp['train'])<=10:
                msg = ""
                templates=[]
                for train in resp['train']:
                    temp={
                    "title": "{}({})".format(train["name"],train["number"]),
                    "subtitle": "arrival:{} departure:{}".format(train["dest_arrival_time"],train["src_departure_time"]),
                    "image_url":"http://srv5.indiarailinfo.com/kjfdsuiemjvcya/0/1978394/0/img60454972968.jpg",
                    "buttons": [
                    {
                    "payload": "flow_C8CA58B61AA0419090AD75EBEA77289F",
                    "title": "Train Route",
                    "type": "postback"
                    },
                    {
                    "payload": "flow_690DBB7EF321481E8110082BD44FBF73",
                    "title": "Seat Availability",
                    "type": "postback"
                    }
                    ]}
                templates.append(temp)
                result = {
                "data": {
                "type": "carousel",
                "templates": templates
                }
                }
                return json.dumps(result)

            msg = ""
            for train in resp['train']:
                msg = "{}\n{}({})\ndep time:{} arr time:{}".format(msg,train['name'],train['number'],train['src_departure_time'],train['dest_arrival_time'])
        else:
            msg="Something went wrong. Try again later"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
        return json.dumps(result)
    else:
        result = { 'data':{'type':'text', 'text':"Source or Destination names incorrect. Try something else" }}
        return json.dumps(result)

@app.route('/seat_availability/<train_num>/<src>/<dst>/<date>')
def check_seat(train_num,src,dst,date):
    try:
        if src in stn_code and dst in stn_code:
            src=stn_code[src]
            dst=stn_code[dst]
            r = requests.get('http://api.railwayapi.com/v2/check-seat/train/{}/source/{}/dest/{}/date/{}/class/SL/quota/GN/apikey/{}/'.format(train_num,src,dst,date,apikey))
            resp = r.json()
            if resp['response_code'] == 200 :
                msg = "{}".format(resp['train_name'])
                for train in resp['availability']:
                    msg = "{}\n{} - {}".format(msg,train['date'],train['status'])
            else:
                msg="Something went wrong. Try again later"
            result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
            return json.dumps(result)
    except Exception as e:
        msg="API's are down. Try again later"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
        return json.dumps(result)

@app.route('/arrivals/<src>/<hrs>')
def train_arrival(src,hrs):
    if src in stn_code:
        src=stn_code[src]
        r = requests.get('http://api.railwayapi.com/v2/arrivals/station/{}/hours/{}/apikey/{}/'.format(src,hrs,apikey))
        resp = r.json()
        if resp['response_code'] == 200 :
            msg = ""
            templates=[]
            for train in resp['train']:
                temp={
                "title": "{}({})".format(train["name"],train["number"]),
                "subtitle": "arrival:{} departure:{}".format(train["scharr"],train["schdep"]),
                "image_url":"http://srv5.indiarailinfo.com/kjfdsuiemjvcya/0/1978394/0/img60454972968.jpg",
                "buttons": [
                {
                "payload": "flow_C8CA58B61AA0419090AD75EBEA77289F",
                "title": "Train Route",
                "type": "postback"
                },
                {
                "payload": "flow_690DBB7EF321481E8110082BD44FBF73",
                "title": "Seat Availability",
                "type": "postback"
                }
                ]}
                templates.append(temp)
        else:
            msg="Something went wrong. Try again later"
            return json.dumps({ 'data':{'type':'text', 'text':"{}".format(msg) }})
        if len(templates)>10:
            templates=templates[:10]
        result = {
        "data": {
        "type": "carousel",
        "templates": templates
        }
        }
        return json.dumps(result)
    else:
        result = { 'data':{'type':'text', 'text':"Source or Destination names incorrect. Try something else" }}
        return json.dumps(result)


@app.route('/bus_route/<origin>/<destination>/<date>')
def bus_route(origin,destination,date):
    date = date.split('-')
    day = date[0]
    month = date[1]
    year = date[2]

    origin_date=dt.datetime(1970,1,1,23,59,59)
    date = dt.datetime(int(year),int(month),int(day),1,1,1)
    result = ""
    bus_url_bus = base_url_bus.format(transit_mode=transit_modes[0],origin=origin,destination=destination,apikey=api_key,departure_time=int((date - origin_date).total_seconds()))
    r = requests.get(bus_url_bus)
    # print (bus_url_bus)
    resp = r.json()
    bus_details = []
    if resp['status'] == "OK":
        routes = resp['routes']
        # print(json.dumps(routes,indent=4))
        for route in routes:
            try:
                bus_detail_temp = {}
                bus_detail_temp['arrival_time'] = route['legs'][0]['arrival_time']['text']
                bus_detail_temp['departure_time'] = route['legs'][0]['departure_time']['text']
                bus_detail_temp['distance'] = route['legs'][0]['distance']['text']
                bus_detail_temp['duration'] = route['legs'][0]['duration']['text']
                bus_detail_temp['bus_agency'] = route['legs'][0]['steps'][0]['transit_details']['line']['agencies'][0]['name']
                bus_detail_temp['bus_agency_phone'] = route['legs'][0]['steps'][0]['transit_details']['line']['agencies'][0]['phone']
                bus_detail_temp['bus_image'] = route['legs'][0]['steps'][0]['transit_details']['line']['vehicle']['icon']
                bus_detail_temp['type']=route['legs'][0]['steps'][0]['transit_details']['line']['vehicle']['type']
                if(route['legs'][0]['steps'][0]['transit_details']['line']['vehicle']['type'] == "BUS"):
                    bus_details.append(bus_detail_temp)
            except KeyError:
                if(route['legs'][0]['steps'][0]['transit_details']['line']['vehicle']['type'] == "BUS"):
                    bus_details.append(bus_detail_temp)
                continue
    else:
        msg=" Route not found. Try again later"
        result = { 'data':{'type':'text', 'text':"{}".format(msg) }}
    templates=[]
    for bus in bus_details:
        temp={
        "title": "Bus Agengy: {}\n Arrival time: {} \n Departure time:{} \n Distance: {}\n Duration: {}".format(bus['bus_agency'],bus['arrival_time'],bus['departure_time'],bus['distance'],bus['duration']),
        "subtitle": "phone num: {}".format(bus['bus_agency_phone']),
        "image_url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeHBNxXAPZf3jpn7C7gxmAqhl_5u7wii0DPd_qAsT5ITXIEHjp"
        }
        templates.append(temp)
    if len(templates)>10:
        templates=templates[:10]
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    result = json.dumps(result)
    return result

@app.route('/hotels/<place>')
def get_hotels(place):
    hotels = []
    get_place_hotels_url = base_url_hotels.format(place=place,apikey=api_key)
    _response = requests.get(get_place_hotels_url)
    #print(get_place_hotels_url)
    _response = _response.json()
    if (_response['status'] == "OK"):
        results = _response['results']
        for result in results:
            hotel = {}
            try :
                hotel['address'] = result['formatted_address']
                hotel['rating'] = result['rating']
                hotel['name'] = result['name']
                hotel['place_id'] = result['place_id']
                get_place_detail_url = base_url_place_details.format(placeid=result['place_id'],apikey=apikey)
                response_place_detail = requests.get(get_place_detail_url)
                response_place_detail = response_place_detail.json()
                if(response_place_detail['status']=="OK"):
                    photoreference = response_place_detail['result']['photos'][0]['photo_reference']
                    hotel['image']=base_url_place_photo.format(photoreference=photoreference,apikey=apikey)
                hotels.append(hotel)
            except KeyError:
                hotels.append(hotel)
                continue

    else:
        return hotels.append("No hotel found in this places")
    templates=[]
    for hotel in hotels:
        temp={
        "title": "Name: {}\n Rating: {} ".format(hotel['name'],hotel['rating']),
        "subtitle": "Address: {}".format(hotel['address']),
        "image_url":"http://ahdzbook.com/data/out/111/hdwp694012313.jpg"
        }
        templates.append(temp)
    if len(templates)>10:
        templates=templates[:10]
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/restaurant/<place>')
def get_restaurant(place):
    hotels = []
    get_place_restaurant_url = base_url_restaurant.format(place=place,apikey=api_key)
    _response = requests.get(get_place_restaurant_url)
    # print(get_place_restaurant_url)
    _response = _response.json()
    if (_response['status'] == "OK"):
        results = _response['results']
        for result in results:
            hotel = {}
            try :
                hotel['address'] = result['formatted_address']
                hotel['rating'] = result['rating']
                hotel['name'] = result['name']
                hotel['place_id'] = result['place_id']
                get_place_detail_url = base_url_place_details.format(placeid=result['place_id'],apikey=apikey)
                response_place_detail = requests.get(get_place_detail_url)
                response_place_detail = response_place_detail.json()
                if(response_place_detail['status']=="OK"):
                    photoreference = response_place_detail['result']['photos'][0]['photo_reference']
                    hotel['image']=base_url_place_photo.format(photoreference=photoreference,apikey=apikey)
                hotels.append(hotel)
            except KeyError:
                hotels.append(hotel)
                continue

    else:
        return hotels.append("No hotel found in this places")
    templates=[]
    for hotel in hotels:
        temp={
        "title": "Name: {}\n Rating: {} ".format(hotel['name'],hotel['rating']),
        "subtitle": "Address: {}".format(hotel['address']),
        "image_url":"https://www.omnihotels.com/-/media/images/hotels/bospar/restaurants/bospar-omni-parker-house-parkers-restaurant-1170.jpg"
        }
        templates.append(temp)
    if len(templates)>10:
        templates=templates[:10]
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/atm/<place>')
def get_ATM(place):
    ATMS = []
    get_place_ATM_url = base_url_ATM.format(place=place,apikey=api_key)
    _response = requests.get(get_place_ATM_url)
    # print(get_place_ATM_url)
    _response = _response.json()
    if (_response['status'] == "OK"):
        results = _response['results']
        for result in results:
            ATM = {}
            try :
                ATM['address'] = result['formatted_address']
                ATM['rating'] = result['rating']
                ATM['name'] = result['name']
                ATM['place_id'] = result['place_id']
                get_place_detail_url = base_url_place_details.format(placeid=result['place_id'],apikey=apikey)
                response_place_detail = requests.get(get_place_detail_url)
                response_place_detail = response_place_detail.json()
                if(response_place_detail['status']=="OK"):
                    photoreference = response_place_detail['result']['photos'][0]['photo_reference']
                    ATM['image']=base_url_place_photo.format(photoreference=photoreference,apikey=apikey)
                ATMS.append(ATM)
            except KeyError:
                ATMS.append(ATM)
                continue
    else:
        return hotels.append("No hotel found in this places")
    templates=[]
    for atm in ATMS:
        if 'name' in atm:
            temp={
            "title": "Name: {}\n Rating: {} ".format(atm['name'],atm['rating']),
            "subtitle": "Address: {}".format(atm['address']),
            "image_url":"https://130e178e8f8ba617604b-8aedd782b7d22cfe0d1146da69a52436.ssl.cf1.rackcdn.com/black-box-atm-attacks-emerging-threat-showcase_image-5-a-9056.jpg"
            }
            templates.append(temp)
    if len(templates)>10:
        templates=templates[:10]
    result = {
    "data": {
    "type": "carousel",
    "templates": templates
    }
    }
    return json.dumps(result)

@app.route('/api/movie_quote')
def get_movie_quote():
    headers = {'X-Mashape-Key':'rrSCvPiswAmshEsCgueXZQl3ixUVp1tS9oFjsnVWHH39DqRk2o'}
    r = requests.get('https://andruxnet-random-famous-quotes.p.mashape.com/' ,headers=headers)
    json_data = json.loads(r.text)
    result = { 'data':{'type':'text', 'text':"{}".format(json_data['quote']) }}
    return json.dumps(result)

@app.route('/api/quote')
def get_quote():
    headers = {'X-Mashape-Key':'9AB6zZ89qsmsheNymbXIbMktTP4pp1ShgiGjsn6h87SAadfhrX' , 'Authorization':'Token token=yd8WzkWNEEzGtqMSgiZBrwtt'}
    r = requests.get('https://juanroldan1989-moviequotes-v1.p.mashape.com/api/v1/quotes' , headers=headers)
    json_data = json.loads(r.text)
    result = { 'data':{'type':'carousel', "templates":[{"title":"{}".format(json_data[5]['content']) , "image_url":"{}".format(json_data[5]['image_large_url'])}] }}
    return json.dumps(result)

@app.route('/api/newquiz/<category>/<level>')
def get_newquiz(category,level):
    data = quiz_json[category][level]
    rand_num=randint(0, 9)
    option=[]
    if (data[rand_num]['correct'] - 1) == 0:
        option.append({"text":data[rand_num]['option'][0] , "postback":"flow_1E815387293141819B651895C17A1BB8"})
    else:
        option.append({"text":data[rand_num]['option'][0] , "postback":"flow_0D741EC17C654E6DA8E0610DBD002FD8"})
    if (data[rand_num]['correct'] - 1) == 1:
        option.append({"text":data[rand_num]['option'][1] , "postback":"flow_1E815387293141819B651895C17A1BB8"})
    else:
        option.append({"text":data[rand_num]['option'][1] , "postback":"flow_0D741EC17C654E6DA8E0610DBD002FD8"})
    result = { 'data':{'type':'msg_options',"text":"{}".format(', '.join(data[rand_num]['quiz'])) , "options":option   }}
    return json.dumps(result)

@app.route('/api/quiz/<category>/<level>')
def get_quiz(category,level):
    if category == 'ES':
        first_rand=0
    elif category == 'gre':
        first_rand=1
    elif category == 'toefl':
        first_rand=2
    second_rand=10-level
    third_rand=randint(0, 9)
    option=[]
    if (quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['correct'] - 1) == 0:
        option.append({"text":quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['option'][0] , "postback":"flow_1E815387293141819B651895C17A1BB8"})
    else:
        option.append({"text":quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['option'][0] , "postback":"flow_0D741EC17C654E6DA8E0610DBD002FD8"})
    if (quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['correct'] - 1) == 1:
        option.append({"text":quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['option'][1] , "postback":"flow_1E815387293141819B651895C17A1BB8"})
    else:
        option.append({"text":quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['option'][1] , "postback":"flow_0D741EC17C654E6DA8E0610DBD002FD8"})
    result = { 'data':{'type':'msg_options',"text":"{}".format(', '.join(quiz_json[first_rand]['quizes'][second_rand]['quizlist'][third_rand]['quiz'])) , "options":option   }}
    return json.dumps(result)

if __name__ == "__main__":
    app.run(host='localhost')
