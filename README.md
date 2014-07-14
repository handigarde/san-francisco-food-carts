san-francisco-food-carts
========================

Find Food Carts/Trucks in SF

Note for setting up Rtree and flask:  
-Set up virtual environment: . venv/bin/activate  
-Install spatiallib (needed for Rtree) - information for spatiallib can be found at http://toblerity.org/rtree/install.html  
-Install Rtree: easy_install Rtree  
-Install flask: pip install flask  
-Launch application: python application.py  
-You're good to go  

This project has been created for validation for a back-end track application to https://www.uber.com/  

Information regarding technologies used:  
-Python was chosen as the primary language for the back-end due to my familiarity with the language, Flask, being a well-known framework for building APIs was the best choice for building the framework itself. This required some work, as my familiarity with Flask prior to starting this application did not stretch far beyond a basic "Hello World" application and definitely did not include any knowledge of parsing/sending JSON objects.  
-Basic HTML/CSS/Javascript were used for the front end, with a CSS library pulled from bootswatch (http://bootswatch.com/slate/). A large difficulty with setting this up was a lack of familiarity with web front-end technologies. Most code included in the front end has been based off of google tutorials for the google maps API or from various questions posted to stackoverflow.com