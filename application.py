#!/usr/bin/python

import sys
import requests
from bs4 import BeautifulSoup

home_html_page = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
base_url = "https://en.wikipedia.org"
movie_lists = []


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

        except Exception as ex:
            pass
        # break

    print("Successfully scrape data from wikipedia")
