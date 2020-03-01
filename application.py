#!/usr/bin/python

import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import sqlite3
import csv


home_html_page = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
base_url = "https://en.wikipedia.org"
movie_lists = []
SQLITE_DATABASE = "movieinfo.db"


# This method scraped data from wikipedia. From individual link it will scrape 10 information for individual movie
def scrape_data_from_wikipedia():
    get_request = requests.get(home_html_page)
    parsed_html = BeautifulSoup(get_request.content, features="html.parser")
    table = parsed_html.select(".wikitable.sortable")
    film_list = table[0].select("tr")

    for single_film in film_list[1:]:
        try:
            film_year = single_film.find_all('a')[1].text
            film_name = single_film.find_all('a')[0].text
            film_awards = single_film.find_all('td')[2].text
            film_nominations = single_film.find_all('td')[3].text

            full_film_link = base_url + single_film.find('a')["href"]
            film_link = single_film.find('a')["href"]
            film = {
                "name": film_name,
                "year": film_year,
                "link": film_link,
                "full_link": full_film_link,
                "awards": film_awards,
                "nominations": film_nominations.rstrip("\n\r"),
            }
            # print(film)
            movie_page = requests.get(full_film_link)
            movie_page_parsed_html = BeautifulSoup(
                movie_page.content, features="html.parser")
            single_movie_table = movie_page_parsed_html.select(
                ".infobox.vevent")
            items = single_movie_table[0].find_all("tr")
            # print("=======================================")
            single_movie_inner_info = []
            for index in range(0, 10):
                try:
                    name = items[index].find("th").text.strip(
                        "\n\r").replace("\n", ' ')
                    value = items[index].find("td").text.strip(
                        "\n\r").replace("\n", ' ')
                    single_movie_inner_info.append({
                        "name": name,
                        "value": value,
                    })
                except Exception as ex:
                    pass

            single_movie_complete_info = {
                'film_info': film,
                'film_inner_info': single_movie_inner_info
            }

            movie_info_store_in_db(single_movie_complete_info)

        except Exception as ex:
            pass
        # break

    print("Successfully scrape data from wikipedia")


# Initialization 3 databases - movies, movie-info and movie_rating for storing data from sraped data
def init_database():
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    init_cursor = db_conn.cursor()
    init_cursor.execute('''DROP TABLE IF EXISTS movies;''')
    init_cursor.execute('''DROP TABLE IF EXISTS movie_info;''')
    init_cursor.execute('''DROP TABLE IF EXISTS movie_rating;''')

    init_cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    year TEXT NOT NULL,
    link TEXT NOT NULL,
    full_link TEXT NOT NULL,
    awards TEXT NOT NULL,
    nominations TEXT NOT NULL
    );
    ''')

    init_cursor.execute('''
    CREATE TABLE IF NOT EXISTS movie_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT NOT NULL,

    movie_id INTEGER NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies (id)
    );
    ''')

    init_cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie_rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rating TEXT NULL,

        movie_id INTEGER NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
        );
        ''')
    db_conn.commit()
    db_conn.close()
    return "Successfully Database Initialization"


# This method stored scraped data into database
def movie_info_store_in_db(single_movie_complete_info):
    print(single_movie_complete_info)
    # print(single_movie_complete_info['film_info'])
    # print(single_movie_complete_info['film_inner_info'])

    db_conn = sqlite3.connect(SQLITE_DATABASE)
    movie_cursor = db_conn.cursor()
    movie_cursor.execute('INSERT INTO movies (name, year, link, full_link, awards, nominations) VALUES (?,?,?,?,?,?)', [
        single_movie_complete_info['film_info']['name'],
        single_movie_complete_info['film_info']['year'],
        single_movie_complete_info['film_info']['link'],
        single_movie_complete_info['film_info']['full_link'],
        single_movie_complete_info['film_info']['awards'],
        single_movie_complete_info['film_info']['nominations'],
    ])

    for info in single_movie_complete_info['film_inner_info']:
        cur = db_conn.cursor()
        cur.execute('INSERT INTO movie_info (name, value, movie_id) VALUES (?,?,?)', [
            info['name'],
            info['value'],
            movie_cursor.lastrowid
        ])

    db_conn.commit()
    db_conn.close()


def dict_factory(cursor, row):
    obj_dict = {}
    for idx, col in enumerate(cursor.description):
        obj_dict[col[0]] = row[idx]
    return obj_dict


# This method will check movie information in scraped data and movies.csv & ratings,csv and insert ratings info into existings scraped database
def Check_Movie_Info_In_CSV():
    csv_file = csv.reader(open('movies.csv', encoding="utf8"), delimiter=",")
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    db_conn.row_factory = dict_factory
    cur = db_conn.cursor()

    try:
        for row in csv_file:
            search_key = row[1].split("(")[0].strip("\n\r")
            cur.execute('select * from movies where name like ?', [
                '%' + search_key + '%'
            ])
            rows = cur.fetchone()
            db_conn.commit()
            # print(rows)
            average_rating = Get_Movie_Average_Rating(row[0])
            if rows:
                cur.execute('INSERT INTO movie_rating (rating, movie_id) VALUES (?,?)', [
                    average_rating,
                    rows['id'],
                ])
                db_conn.commit()
                db_conn.close()
    except Exception as identifier:
        pass


# This method generate average movie rating and ratings givers based on movies.csv and ratings.csv and insert into existing database
def Get_Movie_Average_Rating(movie_id):
    # movie_average_rating = 4
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    db_conn.row_factory = dict_factory
    cur = db_conn.cursor()
    cur.execute('select * from movies')
    rows = cur.fetchall()

    try:
        for movie_row in rows:
            movieId = None
            with open('movies.csv', encoding='utf8') as movieFile:
                movie_info_dictionary = csv.dict_reader(movieFile)
                for row in movie_info_dictionary:
                    if row['title'].split(' (')[0] == movie_row['name']:
                        movieId = row['movieId']

            if movieId:
                with open('ratings.csv', encoding='utf8') as ratingFile:
                    rating_info_dictionary = csv.dict_reader(ratingFile)
                    rating_givers = []
                    ratings = []
                    for row in rating_info_dictionary:
                        if movieId == row['movieId']:
                            rating_givers.append(row['userId'])
                            ratings.append(float(row['rating']))

            def get_average_of_list(list):
                return sum(list) / len(list)

            db_conn = sqlite3.connect(SQLITE_DATABASE)
            db_conn.row_factory = dict_factory
            movie_cursor = db_conn.cursor()
            movie_cursor.execute('INSERT INTO movie_info (name, value, movie_id) VALUES (?,?,?)', [
                'rating_givers',
                len(rating_givers),
                movie_row['id']
            ])
            movie_cursor.execute('INSERT INTO movie_info (name, value, movie_id) VALUES (?,?,?)', [
                'agerage_rating',
                get_average_of_list(ratings),
                movie_row['id']
            ])

            db_conn.commit()
            db_conn.close()

    except Exception as identifier:
        pass


app = Flask(__name__)
@app.route('/')
def home():
    return "This project currently developed  on Python restfull web service under Windows Os. This api generate and store List of Academy Award-winning films data from wikipedia and the rest api will help to have this all data."


# This method will provide movies information from the table of academy award winning films
@app.route('/GetMoviesInfo', methods=['GET'])
def Get_Movies_Info():
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    db_conn.row_factory = dict_factory
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM movies')
    rows = cur.fetchall()
    return jsonify(rows)


# This endpoint will provide movies details information by movie id
@app.route('/GetMoviesInfoById/<id>', methods=['GET'])
def Get_Movies_Info_By_Id(id):
    data = []
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    db_conn.row_factory = dict_factory
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM movies where id = ?', [id])
    movie = cur.fetchall()

    cur = db_conn.cursor()
    cur.execute('SELECT * FROM movie_info where movie_id = ?', [id])
    details_info = cur.fetchall()
    data.append({
        "movie": movie,
        "movie_info": details_info,
    })
    return jsonify(data)


# This endpoint will provide movies details information
@app.route('/GetMoviesDetailsInfo', methods=['GET'])
def Get_Movies_DetailsInfo():
    data = []
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    db_conn.row_factory = dict_factory
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM movies')
    rows = cur.fetchall()
    for row in rows:
        cur.execute('SELECT * FROM movie_info where movie_id = ?', [
            row['id']
        ])
        details_info = cur.fetchall()
        data.append({
            "movie": row,
            "movie_info": details_info,
        })
    return jsonify(data)


def main():
    for arg in sys.argv[1:]:
        if arg == "parse":
            print("Scraping Server Running....")
            init_database()
            scrape_data_from_wikipedia()
            Check_Movie_Info_In_CSV()

        elif arg == "serve":
            print("Rest Api Server Running....")
            app.run()

        else:
            print("Please pass-running mode")


if __name__ == "__main__":
    main()
