import urllib,urllib2, json, operator
from rtree import index
from flask import Flask, Response, render_template, jsonify
try:
    from flask.ext.cors import cross_origin
except:
    from flask_cors import cross_origin
#set various global values
CART_API_URL = "http://data.sfgov.org/resource/rqzj-sfat.json?status=APPROVED" #don't advertize carts with expired permits!
NEARBY_LAT_DELTA = 0.005 #latitude difference used to locate nearby carts
NEARBY_LONG_DELTA = 0.005 #longitude difference used to locate nearby carts
CARTS = [] #list of maps containing cart info
TAG_INFO_FILE = "config/tag_info.json"
TAGS_BY_ITEM = {} #List of food items to be used on the front-end
TAGS_BY_TRUCK = {}
IDX = None
#API_KEY is specific to one AWS EC2 instance. Key will need to be changed to run on other hosts
API_KEY='AIzaSyDrxXyrmwzQr6kbt6TKd-9rxvy7qacSG4U'
#note to self - long is probably not the best x coordinate to use, as distance between degrees varies depending on latitude

def load_category_tags(file_location):
    #set TAGS_BY_ITEM
    json_file = open(file_location)
    return json.load(json_file)

def get_distance_address(start_point, end_point):
    distance_url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins="+start_point+"&destinations="+end_point+"&mode=walking&language=en-EN&sensor=false&units=imperial&key="+API_KEY
    result= json.load(urllib.urlopen(distance_url))
    distance = result['rows'][0]['elements'][0]['distance']['text']
    address = result['destination_addresses'][0]
    return distance, address
    
def get_distances_and_addresses(start_point, destinations):
    distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+start_point+"&destinations="
    i=0
    multiplier=0
    distances = []
    addresses = []
    while i < len(destinations):
        temp_distance_url = distance_url+destinations[i]
        i+=1
        for n in range(24):
            if i < len(destinations):
                temp_distance_url = temp_distance_url +'|'+ destinations[i]
            i += 1
        temp_distance_url = temp_distance_url + "&mode=walking&language=en-EN&sensor=false&units=imperial&key="+API_KEY
        try:
            result = json.load(urllib.urlopen(temp_distance_url))
            for address in result['destination_addresses']:
                addresses.append(address)
            for element in result['rows'][0]['elements']:
                distances.append(element['distance']['text'])
        except Exception as ex:
            pass
    return distances, addresses
    

def load_cart_info(url):
    #Create request object to request the aforementioned list
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-type', 'application/x-www-form-CART_API_URLencoded')
    #Make the request and save the results
    res = urllib2.urlopen(req)
    out = res.read()
    #convert JSON to python dict
    allCarts = json.loads(out)
    #remove unnecessary fields and keep only carts with valid latitude/longitude (for showing on map)
    carts = []
    tag_index = {'Anything': []}
    IDX = index.Index()
    for cart in allCarts:
        if 'latitude' in cart:
            temp_cart = {}
            temp_applicant_name = cart['applicant']
            if 'DBA' in temp_applicant_name:
                temp_applicant_name = temp_applicant_name.split('DBA')[-1][1:].strip()
            elif 'dba' in temp_applicant_name:
                temp_applicant_name = temp_applicant_name.split('dba')[-1][1:].strip()               
            temp_cart['applicant'] = temp_applicant_name
            temp_cart['facilitytype'] = cart['facilitytype']
            temp_cart['fooditems'] = cart['fooditems']
            temp_cart['latitude'] = cart['latitude']
            temp_cart['longitude'] = cart['longitude']
            carts.append(temp_cart)
            fooditems = temp_cart['fooditems'].lower()
            tag_index['Anything'].append(len(carts)-1)
            for tag in TAGS_BY_ITEM.keys():
                matched = False
                for item in TAGS_BY_ITEM[tag]:
                    if item in fooditems and not matched and 'except' not in fooditems:
                        matched = True
                        if tag in tag_index:
                            tag_index[tag].append(len(carts)-1)
                        else:
                            tag_index[tag] = [len(carts)-1]
                    
            x = float(temp_cart['longitude'])
            y = float(temp_cart['latitude'])
            #in order to index based on a point, x1 must = x2 and y1 must = y2 (box with no length/width)
            IDX.insert(len(carts)-1,(x,y,x,y))
    return (carts, tag_index, IDX)

def find_nearby_carts(longitude, latitude,index):
    start_point = latitude, longitude
    nearby_box = (longitude - NEARBY_LONG_DELTA, latitude - NEARBY_LAT_DELTA, longitude + NEARBY_LONG_DELTA, latitude + NEARBY_LAT_DELTA)
    matching_indices = list(IDX.intersection(nearby_box))
    return matching_indices


TAGS_BY_ITEM = load_category_tags(TAG_INFO_FILE)
print 'Loading cart info'
CARTS, TAGS_BY_TRUCK, IDX = load_cart_info(CART_API_URL)
print '%d carts loaded' % len(CARTS)
app = Flask(__name__)

@app.route('/')
def showIndex():
    options = {'/location/<lat_long>': 'Pass comma separated latitude,longitude value to get info for nearby carts.Values returned are in the format:{"data": [list of carts containing address, applicant, distance, facilitytype, fooditems, latitude, and longitude]}', '/location/<lat_long>/<category>': 'Returns all carts near comma separated latitude longitude matching a particular category. List of available categories can be found using the /categories option. Results formatted the same as /location/<lat_long>', '/categories': 'Returns categories in format "data"=[list of categories]'}
    return jsonify(options)
    
@app.route('/categories')
@cross_origin()
def showCategories():
    categories = TAGS_BY_TRUCK.keys()
    categories.sort()
    return jsonify(data=categories)
    
@app.route('/truck/<int:index>')
def show_truck_info(index):
    return jsonify(data=CARTS[index])
    
@app.route('/distance/<lat_long>')
def showDistance(lat_long):
    start_point = lat_long
    end_point = '37.7841316511211,-122.39591339799'
    distance_url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins="+start_point+"&destinations="+end_point+"&mode=walking&language=en-EN&sensor=false&units=imperial&key="+API_KEY
    result= json.load(urllib.urlopen(distance_url))
    return jsonify(result)

@app.route('/location/<lat_long>')
@app.route('/location/<lat_long>/<category>')
@cross_origin()
def send_nearby_carts(lat_long, category='Anything'):
    if category not in TAGS_BY_TRUCK:
        return jsonify(data='Valid categories: %s' % str(TAGS_BY_TRUCK.keys()))
    lat_long = lat_long.split(',')
    latitude = float(lat_long[0])
    longitude = float(lat_long[1])
    unsorted_result=[]
    unsorted_result_lat_long=[]
    result_feet = []
    result_miles = []
    for index in find_nearby_carts(longitude, latitude, IDX):
        if index in TAGS_BY_TRUCK[category]:
            unsorted_result.append(CARTS[index])
            unsorted_result_lat_long.append(CARTS[index]['latitude']+','+CARTS[index]['longitude'])
    distances, addresses = get_distances_and_addresses(lat_long[0]+','+lat_long[1], unsorted_result_lat_long)
    if len(distances) == len(unsorted_result):
        for i in range(len(unsorted_result)):
            unsorted_result[i]['distance'] = distances[i]
            unsorted_result[i]['address'] = addresses[i]
            if 'ft' in unsorted_result[i]['distance']:
                result_feet.append(unsorted_result[i])
            else:
                result_miles.append(unsorted_result[i])
        result_feet.sort(key=operator.itemgetter('distance'))
        result_miles.sort(key=operator.itemgetter('distance'))
        result = result_feet + result_miles
    else:
        result = unsorted_result
    return jsonify(data=result)
        
        
app.run(host='0.0.0.0')
