from flask import Flask, jsonify
from flask.ext.mail import Mail, Message
from dogapi import dog_http_api as api
import json, time

api.api_key='24abba2e095d2d227919ffc2db62ad89'
api.application_key='df2649b4f400a253af68d6c8bba1e425e5330fb7'

app = Flask(__name__)

mail = Mail(app)

USERNAME = 'rhandy87@gmail.com' #enter your email address here
PASSWORD = 'signingin' #enter your email password here

app.config.update(
MAIL_SERVER = 'smtp.gmail.com',
MAIL_PORT = 465,
MAIL_USE_SSL = True,
MAIL_USERNAME = USERNAME,
MAIL_PASSWORD = PASSWORD,
MAIL_FAIL_SILENTLY=False,
DEBUG = True)

mail = Mail(app)

def sendEvent():
    #create necessary values for event
    title = 'Event created via Flask'
    text = 'This event was created via a test module using flask'
    tags = ['version:1', 'application:web']
    #create event, store the event ID returned by the API call
    event_id = api.event_with_response(title, text, tags=tags)
    #debug statement: print "\n\nevent_id = %s\n\n" % str(event_id)
    #example event_id = '2399094330515743017'
    time.sleep(0.05) #appears to take an average of 0.05 seconds for created event to be retreivable
    #get dict containing event information
    event_info = api.get_event(event_id)
    #sometimes the event is not retreivable, so try again until it is
    while 'errors' in event_info:
    	time.sleep(0.05)
    	event_info = api.get_event(event_id)
    #debug statement: print "event_info = %s\n\n" % str(event_info)
    #format message to be emailed
    msg = Message(event_info['title'], sender=USERNAME, recipients=[USERNAME])
    msg.body = "Event created via Flask: \n"
    for item in event_info.keys():
    	msg.body = msg.body + '%s: %s\n' % (item, event_info[item])
    #print "\n\nMessage Body:\n%s\n\n" % str(msg.body)
    #send message
    mail.send(msg)
    #return JSON containing info from the raised event
    return jsonify(event_info)

if __name__ == '__main__':
    sendEvent()
