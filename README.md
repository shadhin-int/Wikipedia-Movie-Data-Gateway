# Wikipedia-Movie-Data-Gateway
 
# Dependencies
This project currently developed  on Python restfull web service under Windows Os so to run this project you should have the requirments:

- Python 3.7.3
- Beautiful Soup: (error tolerant) HTML parsing software This software is currently developed using bs4(4.8.2) 
- Other Python modules (requests, sys, Flask, jsonify)

# To install

Make sure you have Python, BeautifulSoup installed

    pip install beautifulsoup4
    pip install Flask    

# Run The Movie API Gateway

- Clone the project from github repository 
    
    `git clone https://github.com/shadhin-int/Movie-API-Gateway.git`
    
- Browse into the repo root directory (cd Movie-API-Gateway)
- Install the requirement(pip install -r requirement.txt)
- Now, follow below instructions,

To fetched and parsed from sources, and inserted into the database, follow below commands

    python application.py parse

To run api server, follow below commands

    python application.py serve