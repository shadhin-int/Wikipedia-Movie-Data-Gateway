# Wikipedia Movie Data Gateway
 
# Dependencies
This project currently developed  on Python restfull web service under Windows OS, to run this project you should have the requirments:

- Python 3.7.3
- Beautiful Soup: (error tolerant) HTML parsing software This software is currently developed using bs4(4.8.2) 
- Other Python modules (requests, sys, Flask, jsonify)

# Installation

Make sure you have Python, BeautifulSoup & Flask installed

    pip install beautifulsoup4
    pip install Flask    

# Run The Movie Data Gateway

- Clone the project from github repository 
    
    `git clone https://github.com/shadhin-int/Wikipedia-Movie-Data-Gateway.git`
    
- Browse into the repo root directory (cd Wikipedia-Movie-Data-Gateway)
- Install the requirement(pip install -r requirements.txt)
- Now, follow below instructions,

To fetched and parsed from sources, and inserted into the database, follow below commands

    python application.py parse
`Note : This command  will drop all the database and scraped data again. Data already scraped so if you want to scraped data again just run this command otherwise don't need to run this command.`

To run api server, follow below commands

    python application.py serve


# API Endpoint defination
    
1. For List of Academy Award-winning films info (Film Name, Year, Awards and Nominations)
    
        http://127.0.0.1:5000/GetMoviesInfo

2. For list of Academy Award-winning films details info(parse 10 data from the right sidebar from individual link)

        http://127.0.0.1:5000/GetMoviesDetailsInfo


3. For list of Academy Award-winning films details info by movie id

         http://127.0.0.1:5000/GetMoviesInfoById/1


# Task
1. Scraped data from  wikipedia from provied link - Done
2. Stored data in SQLite database using Flask - Done
3. A rest api client that will provide Movies info - Done
4. A rest api client that will provide Movies deatils  info - Done
5. A rest api client that will provide Movies info by movies id - Done
5. Generate data from movies.csv and ratings.csv file and store into existing database  - Done
6. Calculate average rating and rating givers for individual movie - Done
