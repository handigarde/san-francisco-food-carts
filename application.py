import urllib2, json
from rtree import index
from flask import Flask, Response, render_template
#set various global values
CART_API_URL = "http://data.sfgov.org/resource/rqzj-sfat.json?status=APPROVED" #don't advertize carts with expired permits!
NEARBY_LAT_DELTA = 0.005 #latitude difference used to locate nearby carts
NEARBY_LONG_DELTA = 0.005 #longitude difference used to locate nearby carts
CARTS = [] #list of maps containing cart info
TAG_INFO_FILE = "config/tag_info.json"
TAGS_BY_ITEM = {} #List of food items to be used on the front-end
TAGS_BY_TRUCK = {}
IDX = None
#note to self - long is probably not the best x coordinate to use, as distance between degrees varies depending on latitude

def load_category_tags(file_location):
    #set TAGS_BY_ITEM
    json_file = open(file_location)
    return json.load(json_file)
    

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
            temp_cart['applicant'] = cart['applicant']
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
                    if item in fooditems and not matched:
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
    tags = TAGS_BY_TRUCK.keys()
    tags.sort()
    return render_template('index.html',categories=tags)
    
@app.route('/categories')
def showCategories():
    return Response(json.dumps(TAGS_BY_TRUCK), mimetype='application/json')
    
@app.route('/truck/<int:index>')
def show_truck_info(index):
    return Response(json.dumps(CARTS[index]), mimetype='application/json')

@app.route('/location/<lat_long>')
@app.route('/location/<lat_long>/<category>')
def send_nearby_carts(lat_long, category='Anything'):
    lat_long = lat_long.split(',')
    latitude = float(lat_long[0])
    longitude = float(lat_long[1])
    result = []
    for index in find_nearby_carts(longitude, latitude, IDX):
        if index in TAGS_BY_TRUCK[category]:
            result.append(CARTS[index])
    return Respone(json.JSONEncoder.encode(result), mimetype='application/json')
        
        
app.run(host='0.0.0.0')