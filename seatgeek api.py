

import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import time
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.notebook_repr_html', True)
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("poster")
from bs4 import BeautifulSoup
import requests
import html5lib
import datetime
import os
import time
import re

today=datetime.date.today()







teams = []

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

r = requests.get("https://en.wikipedia.org/wiki/National_Basketball_Association"  ,verify=False)
text = r.text
soup = BeautifulSoup(text, 'html.parser')




rows = soup.find("table", attrs={"class": "navbox wikitable"}).find_all("td")

rows

for row in rows:
    elements = row.find_all("b")
    for el in elements:
        teams.append(el.text)



r = requests.get("http://api.seatgeek.com/2/events?client_id=xxxxxx'" , verify=False) # put in your seatgeek clinet_id here



count = 0
for team in teams:
    team_lower = team.lower()
    team_final = team_lower.replace(" ", "+")
    r = requests.get('https://api.seatgeek.com/2/events?q='+team_final+'&per_page=1000&client_id=MTQzMjkwMTJ8MTU0NDQ2MTk0NS40Nw', verify=False)
    #r = requests.get('https://api.seatgeek.com/2/events?q=boston+celtics&per_page=1000&client_id=MTQzMjkwMTJ8MTU0NDQ2MTk0NS40Nw', verify=False)
    js = r.json()
    events = js["events"]



    df = pd.DataFrame()

    if count == 0:
        for event in events:
            keys =  event.keys()
            break

    for key in keys:
        lst = []
        listing_count = []
        avg_price = []
        lowest_price_good_deal = []
        lowest_price = []
        highest_price = []
        address = []
        city = []
        country = []
        display_location = []
        extended_address = []
        venueid = []
        location = []
        venuename = []
        postal_code = []
        venuescore = []
        venueslug = []
        state = []
        timezone = []
        url = []
       
        for event in events:
            if key == "stats":
                listing_count.append(event[key]["listing_count"])
                avg_price.append(event[key]["average_price"])
                lowest_price_good_deal.append(event[key]["lowest_price_good_deals"])
                lowest_price.append(event[key]["lowest_price"])
                highest_price.append(event[key]["highest_price"])
            elif key == "venue":
                address.append(event[key]["address"])
                city.append(event[key]["city"])
                country.append(event[key]["country"])
                display_location.append(event[key]["display_location"])
                extended_address.append(event[key]["extended_address"])
                venueid.append(event[key]["id"])
                location.append(event[key]["location"])
                venuename.append(event[key]["name"])
                postal_code.append(event[key]["postal_code"])
                venuescore.append(event[key]["score"])
                venueslug.append(event[key]["slug"])
                state.append(event[key]["state"])
                timezone.append(event[key]["timezone"])
                url.append(event[key]["url"])
            else:
                lst.append(event[key])
        if key == "stats":
            df["listing_count"] = listing_count
            df["avg_price"] = avg_price
            df["lowest_price_good_deal"] = lowest_price_good_deal
            df["lowest_price"] = lowest_price
            df["highest_price"] = highest_price
        elif key == "venue":
            df["address"] = address
            df["city"] = city
            df["country"] = country
            df["display_location"] = display_location
            df["extended_address"] = extended_address
            df["venueid"] = venueid
            df["location"] = location
            df["venuename"] = venuename
            df['postal_code'] = postal_code
            df["venuescore"] = venuescore
            df["venueslug"] = venueslug
            df["venuestate"] = state
            df["venuetimezone"] = timezone
            df['url'] = url
        else:
            df[key] = lst

    if count == 0:
        fulldf = df
    else:
        fulldf = fulldf.append(df, ignore_index = True)
    count = count + 1


# clean the data
# rename score as ticketscore to distinguish it from other scores



fulldf=fulldf.rename(columns = {'score':'ticket_score'})

# make sure you only have nba games
fulldf = fulldf.loc[fulldf['type'] == "nba"]
# get rid of the all-star game
fulldf = fulldf.loc[fulldf['title'] != "NBA All-Star Game"]
fulldf = fulldf.loc[fulldf['title'] != "NBA All-Star Celebrity Game"]
fulldf = fulldf.loc[fulldf['title'] != "NBA All-Star Rising Stars Challenge"]

# drop unnecessary columns
fulldf = fulldf.drop("time_tbd", 1)
fulldf = fulldf.drop("taxonomies", 1)
fulldf = fulldf.drop("links", 1)
fulldf = fulldf.drop("url", 1)
fulldf = fulldf.drop("display_location", 1)
fulldf = fulldf.drop("venueslug", 1)
fulldf = fulldf.drop("venuetimezone", 1)
fulldf = fulldf.drop("date_tbd", 1)
fulldf = fulldf.drop("type", 1)
fulldf = fulldf.drop("location", 1)
fulldf = fulldf.drop("conditional", 1)




#teams_playing = fulldf.title
#away_teams = []
#home_teams = []
#for teams_pl in teams_playing:
#    split = teams_pl.split(" at ")
#    away_teams.append(split[0])
#    home_teams.append(split[1])
#    
#fulldf["home_team"] = home_teams
#fulldf["away_team"] = away_teams
##fulldf = fulldf.drop("title", 1)


# calculate days away
datetimes = fulldf["datetime_utc"]
date = []
timeutc = []
daysaway = []
toddate = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d").date()

for dattime in datetimes:
    futdate = datetime.datetime.strptime(dattime.split("T")[0],"%Y-%m-%d").date()
    timeaway = futdate - toddate
    daysaway.append(int(timeaway.days))
    date.append(dattime.split("T")[0])
    timeutc.append(dattime.split("T")[1])
fulldf["dateutc"] = date
fulldf["timeutc"] = timeutc
fulldf["daysaway"] = daysaway
# sources: http://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/

# reset index
fulldf = fulldf.reset_index()

fulldf = fulldf.drop(['index'], axis=1)

fulldf = fulldf.iloc[fulldf.astype(str).drop_duplicates().index]

fulldf[['away_team','home_team']] = fulldf['title'].str.split(' at ',expand=True)

fulldf['title'] = fulldf['short_title']

# save as a CSV
fulldf.to_csv("ticket_price" + str(today) + ".csv")
# sources: http://chrisalbon.com/python/pandas_saving_dataframe_as_csv.html
