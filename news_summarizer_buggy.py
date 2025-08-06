import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import logging


BASE_URL = "https://newsapi.org/v1/articles"
#Since newsapi v1 returns null for time published, we will have to use newsapi v2 to get date published.
FILTER_URL = "https://newsapi.org/v2/everything"

#Format the log level and what the log will show in console
logging.basicConfig(level=logging.ERROR, format='%(levelname)s : %(message)s')


def get_articles(filters):
    if filters:
        filter_string = "&".join(filters)
        url = f"{FILTER_URL}?{filter_string}&sources=bbc-news&apiKey={os.getenv("API_KEY")}"
    else:
        url = f"{BASE_URL}?source=bbc-news&apiKey={os.getenv("API_KEY")}"
    response = requests.get(url)
    try:
        #response.raise_for_status() to create an HTTPError object if the response status code is not in 200-299 range. 
        response.raise_for_status()
        articles = response.json()['articles']
        return articles
    except requests.exceptions.HTTPError as req_e:
        #print("Failed to fetch news\n")
        logging.exception(f"HTTP error: {req_e.response.status_code}")
        #print(f"HTTP error: {req_e.response.status_code}")
        return []

def get_keyword(filter_arr):
    user_keyword_choice = input("Would you like to filter articles by keyword? (type yes to filter by keyword else type no to not filter by keyword)\n")
    if user_keyword_choice.lower() != "yes" and user_keyword_choice.lower() != "no":
        while True:
            user_keyword_choice = input("Error. Wrong input. Please enter yes or no only\n")
            if user_keyword_choice.lower() == "yes" or user_keyword_choice.lower() == "no":
                break
    if user_keyword_choice.lower() == "yes":
        keyword_str = input("Enter the keyword you would like the articles presented to include:\n")
        filtered_keyword_str = "q=" + keyword_str
        filter_arr.append(filtered_keyword_str)
        print("Keywords included. Moving to date range finder.")
    else:
        print("Keywords inclusion skipped. Moving to date range finder.")

def get_date_range(filter_arr):
    user_date_range_choice = input("Would you like to filter articles by include a from and to date? (type yes to filter by date range else type no to not filter by date)\n")
    if user_date_range_choice.lower() != "yes" and user_date_range_choice.lower() != "no":
        while True:
            user_date_range_choice = input("Error. Wrong input. Please enter yes or no only\n")
            if user_date_range_choice.lower() == "yes" or user_date_range_choice.lower() == "no":
                break
    if user_date_range_choice.lower() == "yes":
        while True:
            from_date_str = input("Enter the start date to search from in (YYYY-MM-DD) format\n")
            try:
                from_date_datetime = datetime.strptime(from_date_str,"%Y-%m-%d")
                #Date entered is ahead of today's date.
                if from_date_datetime.date() > datetime.today().date():
                    while from_date_datetime.date() > datetime.today().date():
                        from_date_str = input("Date entered is ahead of today's date. Please enter another date in (YYYY-MM-DD format)\n")
                        try:
                            from_date_datetime = datetime.strptime(from_date_str,"%Y-%m-%d")
                        except ValueError as new_from_ve:
                            logging.exception("Invalid date entered. Try again by providing the correct date in the specified format")
                print(f"From Date: {from_date_datetime.date()}")
                break
            except ValueError as date_ve:
                print(f"Error: {date_ve}")
                print("Invalid date. Try again by providing the correct date in the specified format")
        while True:
            to_date_str = input("Enter the end date of the search in (YYYY-MM-DD) format\n")
            try:
                to_date_datetime = datetime.strptime(to_date_str,"%Y-%m-%d")
                if to_date_datetime.date() > datetime.today().date():
                    while to_date_datetime.date() > datetime.today().date():
                        to_date_str = input("Date entered is ahead of today's date. Please enter another date in (YYYY-MM-DD format)\n")
                        try:
                            to_date_datetime = datetime.strptime(to_date_str,"%Y-%m-%d")
                        except ValueError as new_to_ve:
                            logging.exception("Invalid date entered. Try again by providing the correct date in the specified format")
                print(f"To Date: {to_date_datetime.date()}")
                if to_date_datetime < from_date_datetime:
                    while to_date_datetime < from_date_datetime:
                        to_date_str = input("Article search end date cannot be before the Article search start date. Please enter a vaild end date in (YYYY-MM-DD) format.\n")
                        try:
                            to_date_datetime = datetime.strptime(to_date_str,"%Y-%m-%d")
                            print(f"New To Date: {to_date_datetime.date()}")
                        except ValueError as new_ve:
                            print(f"Error: {new_ve}")
                            print("Invalid date. Try again by providing the correct date in the specified format")
                break
            except ValueError as date_ve:
                print(f"Error: {date_ve}")
                print("Invalid date. Try again by providing the correct date in the specified format")
        from_date_filter = "from=" + str(from_date_datetime)
        to_date_filter = "to=" + str(to_date_datetime)
        filter_arr.append(from_date_filter)
        filter_arr.append(to_date_filter)

# def get_filtered_articles(filter_arr):
#     filter_string = "&".join(filter_arr)
#     url = f"{FILTER_URL}?{filter_string}&sources=bbc-news&apiKey={os.getenv("API_KEY")}"
#     response = requests.get(url)
#     try:
#         #response.raise_for_status() to create an HTTPError object if the response status code is not in 200-299 range. 
#         response.raise_for_status()
#         articles = response.json()['articles']
#         return articles
#     except requests.exceptions.HTTPError as req_e:
#         #print("Failed to fetch news\n")
#         logging.exception(f"HTTP error: {req_e.response.status_code}")
#         #print(f"HTTP error: {req_e.response.status_code}")
#         return []
    

def summarize(articles):
    for art in articles:
        print("Title:", art['title'])
        print("Description:", art['description'])
        print("URL:", art['url'])
        print("----")


def main():
    try:
        load_dotenv()
        filters = []
        get_keyword(filters)
        get_date_range(filters)
        #check if the user has specific filters for articles. If no then execute the original function.
        # if filters:
        #     filtered_articles = get_filtered_articles(filters)
        #     if filtered_articles:
        #         summarize(filtered_articles)
        # else:
        articles = get_articles(filters)
        if articles:
            summarize(articles)
    except Exception:
        logging.exception("Something went wrong")
        # print(f"\nSomething went wrong: {type(art_e)}")
        # print(art_e)


main()
