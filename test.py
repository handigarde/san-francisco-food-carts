import json, urllib, unittest

#global variable for API address
api_address = 'http://54.186.126.107:5000'

class TestCartAPI(unittest.TestCase):
    def setup(self):
        pass

    def test01ValidCallByLocation(self):
        """
        test valid call to the API using a proper latitude,longitude variable
        """
        url = api_address + '/location/37.7823601210175,-122.402095994563'
        try:
            results = json.load(urllib.urlopen(url))['data']
            self.assertTrue('applicant' in results[0] and 'fooditems' in results[0] and 'latitude' in results[0])
        except ValueError:
            self.fail(msg='JSON response not received from API')
        except Exception as e:
            self.fail(msg='Unexpected error received: %s' % str(e.message))

    def test02InvalidCallByLocation(self):
        """
        test invalid call to the API - attempt passing non-numeric value as longitude
        """
        url = api_address + '/location/7823601210175,Tex-mex'
        try:
            results = json.load(urllib.urlopen(url))
            self.fail(msg="Result should not have been JSON (HTTP 500 expected)")
        except ValueError as e:
            #we want a value error, JSON should not be returned
            pass
        except Exception as e:
            self.fail(msg='Unexpected error received: '+e.message)
            
    def test03ValidCallWithCategory(self):
        """
        test valid call to the API using latitude,longitude variable and specify filter category
        """
        url = api_address + '/location/37.7823601210175,-122.402095994563/Beverages'
        try:
            results = json.load(urllib.urlopen(url))['data']
            self.assertTrue('applicant' in results[0] and 'fooditems' in results[0] and 'latitude' in results[0])
        except ValueError:
            self.fail(msg='JSON response not received from API')
        except Exception as e:
            self.fail(msg='Unexpected error received: %s' % e.message)
            
    def test04InvalidCallWithCategory(self):
        """
        test invalid call to the API using proper latitue,longitude variable and use an invalid filter category
        """
        url = api_address + '/location/37.7823601210175,-122.402095994563/Eats'
        try:
            results = json.load(urllib.urlopen(url))['data']
            self.assertTrue('Valid categories' in results)
        except ValueError:
            self.fail(msg='JSON response not received from API')
        except Exception as e:
            self.fail(msg='Unexpected error received: %s' % e.message)
            

if __name__ == '__main__':
    unittest.main()
    
