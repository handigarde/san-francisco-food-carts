from dogapi import dog_http_api as api

if __name__ == '__main__':
    api.api_key='24abba2e095d2d227919ffc2db62ad89'
    api.application_key='df2649b4f400a253af68d6c8bba1e425e5330fb7'
    #create necessary values for event
    title = 'This event was created via the dog_http_api'
    text = '@rhandy87@gmail.com This event was created via a test module using dog_http_api'
    tags = ['version:1', 'application:web']
    #create event, store the event ID returned by the API call
    event_id = api.event_with_response(title, text, tags=tags)