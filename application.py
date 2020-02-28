#!/usr/bin/python

import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import sqlite3

home_html_page = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
base_url = "https://en.wikipedia.org"
movie_lists = []
SQLITE_DATABASE = "movieinfo.db"


def scrape_data_from_wikipedia():
    init_database()

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


def init_database():
    db_conn = sqlite3.connect(SQLITE_DATABASE)
    init_cursor = db_conn.cursor()
    init_cursor.execute('''DROP TABLE IF EXISTS movies;''')
    init_cursor.execute('''DROP TABLE IF EXISTS movie_info;''')

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
    db_conn.commit()
    db_conn.close()
    return "Successfully Database Initialization"


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


def main():
    for arg in sys.argv[1:]:
        if arg == "parse":
            print("Scraping Server Running....")
            scrape_data_from_wikipedia()
        else:
            print("Please pass-running mode")


if __name__ == "__main__":
    main()
