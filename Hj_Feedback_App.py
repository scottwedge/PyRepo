# import packages
import numpy as np
import json
import requests
import pandas as pd
import timeit
import math
import datetime
import os
import time
import csv
import plotly.express as px
import streamlit as st

# options
pd.set_option("display.precision", 3)
pd.options.display.float_format = '{:.4f}'.format

np.set_printoptions(precision=4, suppress=True)

st.title("HotJar Feedback Analysis")
df = pd.read_csv('feedback-256010.csv')

kvp = {"Ab" : "ab.rockwellautomation", "RA" : "www.rockwellautomation.com","RA/my" : "www.rockwellautomation.com/my","PCDC" : "compatibility.rockwellautomation","Account" : "www.rockwellautomation.com/account/","DL" : "download.rockwellautomation.com","Search" : "rockwellautomation.com/search","[All Feedback]" : ""}
#URLs to consider:
#"ab.rockwellautomation"
#"www.rockwellautomation.com"
#"www.rockwellautomation.com/my"
#"compatibility.rockwellautomation"
#"www.rockwellautomation.com/account/"
#'rockwellautomation.com/search'

urlch = st.selectbox("Choose a URL to analyze:", options=list(kvp.keys()))
url = kvp[urlch]

down_df = df[df['Source URL'].str.contains(url)]

tmrange = st.slider("Week range:", min_value=1,max_value=52,step=1)
from datetime import datetime, timedelta
import pytz

today = datetime.now()
timzo = pytz.timezone('US/Eastern')
today = timzo.localize(today)
week_prior = today - timedelta(weeks=tmrange)
week_prior

down_df['Date Submitted'] = pd.to_datetime(down_df['Date Submitted'])
down_df['Date Submitted']=down_df['Date Submitted'].dt.tz_localize(tz='US/Eastern', nonexistent='shift_forward')
date_df = down_df.loc[down_df['Date Submitted'] >= week_prior]
st.write(date_df)

bad_df = date_df.loc[(date_df['Emotion (1-5)'] == 1) | (date_df['Emotion (1-5)'] == 2)]

st.header("What has total feedback recieved for this URL looked like over a span of time?")
histfig = px.histogram(date_df, x='Date Submitted', color='Emotion (1-5)',
                      title='Feedback Responses for url '+'('+str(tmrange)+' weeks)',
                      opacity=0.8,
                       category_orders={'Emotion (1-5)':[1,2,3,4,5]},
                       color_discrete_map={
                           1:"#E45756",
                           2:"#F58518",
                           3:"#BAB0AC",
                           4:"#72B7B2",
                           5:"#54A24B"
                       },
                       nbins=20
                      )
st.plotly_chart(histfig)

st.header("Which Country is submitting the most feedback? How do user experiences across countries match up with each other?")
counfig = px.histogram(date_df, y='Country', color='Emotion (1-5)',
                      title='Breakdown by Country for url given',
                      opacity=0.8,
                       orientation = 'h',
                       height = 1000,
                       category_orders={'Emotion (1-5)':[1,2,3,4,5]},
                       color_discrete_map={
                           1:"#E45756",
                           2:"#F58518",
                           3:"#BAB0AC",
                           4:"#72B7B2",
                           5:"#54A24B"
                       },
                       #nbins=20
                      ).update_yaxes(categoryorder="total ascending")
st.plotly_chart(counfig)

st.header("Where is the bad feedback coming from?")
badperc = px.pie(bad_df, names="Country", hole = .4, title = "% of total bad feedback for url over "+str(tmrange)+" weeks")
st.plotly_chart(badperc)

#pieplot = px.pie(down_df, names="Country", hole = .4, title="All Time Feedback Breakdown by country for "+url)
#st.plotly_chart(pieplot)

mess_df=date_df.loc[date_df["Message"].notna()]
mess_df = mess_df.drop(columns=['Number',"User","Device","OS","Browser"])

mfildic = {"[No filter]" : 1, "People who can't find a product" : 2, "People who can't download" : 3, "People who may require a response" : 4}
kw1 = {1 : [""], 2 : ["find","where","part","no"], 3 : ["cant","looking","find","issues","problem","downloading"], 4 : ["who","where","what","how"]}
kw2 = {1 : [""], 2 : ["part","product"], 3 : ["download", "downloading", "software"], 4 : ["?"]}

st.subheader('Responses over the past '+str(tmrange)+' weeks:')
mfsb = st.selectbox("Filter messages by:", options=list(mfildic.keys()))
for row in mess_df.itertuples():
    if (any(x in row.Message.lower() for x in kw1[mfildic[mfsb]])) and (any(y in row.Message.lower() for y in kw2[mfildic[mfsb]])):
        if row._5 == 3:
            st.info("\"" + row.Message + "\"")
            st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
        elif row._5 >3:
            st.success("\"" + row.Message + "\"")
            st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
        else:
            st.error("\"" + row.Message + "\"")
            st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
