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
-The Rtree data structure was used since searching for points withing a certain distance of a location (as described in http://en.wikipedia.org/wiki/R-tree)  
-Basic HTML/CSS/Javascript were used for the front end, with a CSS library pulled from bootswatch (http://bootswatch.com/slate/). A large difficulty with setting this up was a lack of familiarity with web front-end technologies. Most code included in the front end has been based off of google tutorials for the google maps API or from various questions posted to stackoverflow.com  

Necessary trade-offs made during development:  
-Initial plans included the creation of a database of cart information (i.e. cart applicant, location, items sold, category, etc), however due to the possibility of updating/creating/removing carts on startup, as well as the low volume of total carts, as well as the amount of necessary information per cart, in memory dictionaries sufficed for testing the application  
-Initial plans also included setting up a Redis data store for storing locations and distances to nearby carts in memory (reducing the number of google maps API calls needed). Due to a lack of familiarity with Redis, I was unable to implement this in the given time frame  

For reference to my programming language familiarity and experience, please check my resume at (https://s3.amazonaws.com/R-Handy-Resume/Ryan+Handy+Resume.pdf)  
