import urllib2, json
from rtree import index
from flask import Flask, Response
#set various global values
CART_API_URL = "http://data.sfgov.org/resource/rqzj-sfat.json?status=APPROVED" #don't advertize carts with expired permits!
NEARBY_LAT_DELTA = 0.005 #latitude difference used to locate nearby carts
NEARBY_LONG_DELTA = 0.005 #longitude difference used to locate nearby carts
CARTS = [] #list of maps containing cart info
IDX = None
#note to self - long is probably not the best x coordinate to use, as distance between degress varies depending on latitude

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
            x = float(temp_cart['longitude'])
            y = float(temp_cart['latitude'])
            #in order to index based on a point, x1 must = x2 and y1 must = y2 (box with no length/width)
            IDX.insert(len(carts)-1,(x,y,x,y))
    return (carts, IDX)

def find_nearby_carts(longitude, latitude,index):
    nearby_box = (longitude - NEARBY_LONG_DELTA, latitude - NEARBY_LAT_DELTA, longitude + NEARBY_LONG_DELTA, latitude + NEARBY_LAT_DELTA)
    matching_indices = list(IDX.intersection(nearby_box))
    return matching_indices

print 'Loading cart info'
CARTS, IDX = load_cart_info(CART_API_URL)
print '%d carts loaded' % len(CARTS)
app = Flask(__name__)

@app.route('/location/<lat_long>')
def send_nearby_carts(lat_long):
    lat_long = lat_long.split(',')
    latitude = float(lat_long[0])
    longitude = float(lat_long[1])
    result = []
    for index in find_nearby_carts(longitude, latitude, IDX):
        result.append(CARTS[index])
    return Response(json.dumps(result), mimetype='application/json')
        
        
app.run(host='0.0.0.0')