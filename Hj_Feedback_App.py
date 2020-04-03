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

kvp = {"[All Feedback]" : "","Allen-Bradley" : "ab.rockwellautomation", "Rockwell Automation" : "www.rockwellautomation.com","RA/my" : "www.rockwellautomation.com/my","PCDC" : "compatibility.rockwellautomation",
"Account" : "www.rockwellautomation.com/account/","Download.RA" : "download.rockwellautomation.com","Search" : "rockwellautomation.com/search","Investor Relations" : "ir.rockwellautomation",
"Campaign Pages" : "campaign.rockwellautomation"}
#cskvp = {"[No filter]":"", "English - NA":"en_NA", "Spanish - Central America":"es_CEM", "English - Caribbean":"en_CAR", "Spanish - Caribbean":"es_CAR", "English - Middle East":"en_MDE",
#"English - Sub-Saharan Africa":"en_ZA", "English - Southeast Asia":"en_SEA", "Spanish - Argentina":"es_AR", "Spanish - Mexico":"es_MX", "Portuguese - Brazil":"pt_BR", "Chinese - China":"zh_CN",
#"German - Germany":"de_DE", "Czech - Czech":"cs_CZ", "Spanish - Spain":"es_ES", "French - France":"fr_FR", "English - India":"en_IN", "English - Israel":"en_IL", "Italian - Italy":"it_IT",
#"Japanese - Japan":"ja_JP","Korean - Korea":"ko_KR","Turkish - Turkey":"tr_TR", "English - United Kingdom":"en_GB", "Russian - Russia":"ru_RU"}
ablkvp = {"[No language specified]":"","zh":"/zh/","Deutsch":"/de/","Spanish":"/es/","French":"/fr/","Italian":"/it/","Japanese":"/ja/","Korean":"/ko/","Portuguese":"/pt/"}
tlkeys = {"[No country filter]":1,"NA":2,"EMEA":3,"APAC":4,"LAR":5}
testlist = {1 : [""], 2 : ["en_NA"], 3 : ["cs_CZ","en_UK","nl_BE","da_DK","en_ZA","nl_NL","de_AT","es_ES","pl_PL","de_CH","fr_BE","pt_pt","de_DE","fr_CH","ru_RU","en_IE","fr_FR","sv_SE","en_IL","it_IT","tr_TR","en_MDE"],
4 : ["zh_CN","ja_JP","zh_TW","en_SEA","ko_KR","en_AU","en_NZ","en_IN"], 5 : ["en_CAR","es_CL","es_PE","es_CAR","es_CO"]}
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
#For COuntry sites: df[s.str.contains('og|at')]

if url == "www.rockwellautomation.com":
    cssel = st.selectbox("Choose an RA country site:", options=list(tlkeys.keys()))
    tlindex = tlkeys[cssel]
    down_df = df[df['Source URL'].str.contains('|'.join(testlist[tlindex]))]
elif url == "ab.rockwellautomation":
    cssel = st.selectbox("Choose a region:", options=list(ablkvp.keys()))
    csfil = ablkvp[cssel]
    down_df = df[df['Source URL'].str.contains(csfil)]

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
#st.write(date_df)

bad_df = date_df.loc[(date_df['Emotion (1-5)'] == 1) | (date_df['Emotion (1-5)'] == 2)]

if date_df.empty == True:
    st.write('No data to display.')
else:
    datecut_df = date_df
    ndates = datecut_df['Date Submitted'].dt.normalize().nunique()
    st.header("What has total feedback recieved for this URL looked like over a span of time?")
    histfig = px.histogram(date_df, x='Date Submitted', color='Emotion (1-5)',
        title='Feedback Responses for url '+'('+str(tmrange)+' weeks)',
        opacity=0.8,
        category_orders={'Emotion (1-5)':[1,2,3,4,5]},
        color_discrete_map={1:"#e83b3a",2:"#c97d7d",3:"#BAB0AC",4:"#99bd9c",5:"#4cba76"},
        nbins=tmrange*7
    )
    histfig.update_layout(xaxis_tickformat='%d %B (%a)', xaxis=dict(dtick=86400000.0))
    st.plotly_chart(histfig)
    st.header("Which Country is submitting the most feedback? How do user experiences across countries match up with each other?")
    counfig = px.histogram(date_df, y='Country', color='Emotion (1-5)',
        title='Breakdown by Country for url given',
        opacity=0.8,
        orientation = 'h',
        height = 800,
        category_orders={'Emotion (1-5)':[1,2,3,4,5]},
        color_discrete_map={1:"#e83b3a",2:"#c97d7d",3:"#BAB0AC",4:"#99bd9c",5:"#4cba76"},
        #nbins=20
    ).update_yaxes(categoryorder="total ascending")
    st.plotly_chart(counfig)
    #st.header("Where is the bad feedback coming from?")
    #badperc = px.pie(bad_df, names="Country", hole = .4, title = "% of total bad feedback for url over "+str(tmrange)+" weeks")
    #st.plotly_chart(badperc)
    st.header('Pages of interest: these specific pages have recieved mutiple negative feedbacks')
    apdate_df=date_df
    apdate_df['feedback_count']= apdate_df['Source URL'].map(apdate_df['Source URL'].value_counts())
    bad_df = apdate_df.loc[(apdate_df['Emotion (1-5)'] == 1) | (apdate_df['Emotion (1-5)'] == 2)]
    intr_df = bad_df[bad_df.duplicated(subset='Source URL', keep=False)]
    bdap_df=intr_df
    bdap_df['negative_feedbacks']= bdap_df['Source URL'].map(bdap_df['Source URL'].value_counts())
    if bdap_df.empty == False:
        intrfig = px.scatter(bdap_df, y='Source URL', x='negative_feedbacks', color='negative_feedbacks', height = 800, color_continuous_scale=px.colors.sequential.YlOrRd, size='feedback_count')
        intrfig.update_layout(margin=dict(l=500,r=10,t=10,b=20), xaxis=dict(dtick=1))
        intrfig.layout.coloraxis.showscale = False
        st.plotly_chart(intrfig)
        dd_df = bdap_df.drop_duplicates(subset='Source URL', keep='first')
        nlarg_df = dd_df.nlargest(5,['negative_feedbacks'])
        c = 0
        for i in nlarg_df.itertuples():
            c = c+1
            st.write(str(c)+'. '+str(i._5))
    else:
        st.write("No pages of interest for given filters.")



#pieplot = px.pie(down_df, names="Country", hole = .4, title="All Time Feedback Breakdown by country for "+url)
#st.plotly_chart(pieplot)

mess_df=date_df.loc[date_df["Message"].notna()]
mess_df = mess_df.drop(columns=['Number',"User","OS"])

#from wordcloud import WordCloud, STOPWORDS
#import matplotlib.pyplot as plt
#if mess_df.empty == False:
    #st.header("WordCloud for feedback responses:")
    #cust_swords = ["Rockwell", "Automation"] + list(STOPWORDS)
    #wcloud = WordCloud(background_color="white", scale=2, font_path='calibri',min_font_size=12,max_words=100,stopwords=cust_swords).generate(" ".join(mess_df['Message']))
    #plt.figure(figsize=(20,10))
    #plt.imshow(wcloud, interpolation='bilinear')
    #plt.axis("off")
    #plt.show()
    #st.pyplot()
#else:
    #st.write("No responses for given filters.")

mfildic = {"[No filter]" : 1, "People who can't find a product" : 2, "People who can't download software" : 3, "People who may require a response" : 4}
cfildic = {"[All Countries]" : 1, "United States" : 2, "Mexico" : 3, "China" : 4, "United Kingdom" : 5}
kw1 = {1 : [""], 2 : ["find","where","part","no"], 3 : ["cant","can't","looking","find","issues","problem","downloading","how","nothing","impossible"], 4 : ["who","where","what","how"]}
kw2 = {1 : [""], 2 : ["part","product"], 3 : ["download", "downloading", "software"], 4 : ["?"]}
ckw = {1 : "", 2 : "United States", 3 : "Mexico", 4 : "China", 5 : "Mexico"}

body="Here is a list of responses over the past "+str(tmrange)+" weeks for "+str(url)

from yandex.Translater import Translater
from langdetect import detect

st.subheader('Responses over the past '+str(tmrange)+' weeks:')
mfsb = st.selectbox("Filter messages by:", options=list(mfildic.keys()))
#cfsb = st.selectbox("Filter messages by:", options=list(cfildic.keys()))
counlist = mess_df.Country.unique()
counlist = np.insert(counlist,0,"")
cfsb = st.selectbox("Filter responses by country (leave blank for all feedback):", options=counlist)
for row in mess_df.itertuples():
    if cfsb in str(row.Country):
        if (any(x in row.Message.lower() for x in kw1[mfildic[mfsb]])) and (any(y in row.Message.lower() for y in kw2[mfildic[mfsb]])):
            try:
                detlan = detect(str(row.Message))
            except:
                detlan = 'en'
            if row._7 == 3:
                if detlan == 'en':
                    st.info("\"" + row.Message + "\"")
                else:
                    tr = Translater()
                    tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                    tr.set_text(str(row.Message))
                    tr.set_to_lang('en')
                    mtrans = tr.translate()
                    st.info("\"" + row.Message + "\""+"\nTranslation Attempt: "+"\"" + mtrans + "\"")
                st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)
            elif row._7 >3:
                if detlan == 'en':
                    st.success("\"" + row.Message + "\"")
                else:
                    tr = Translater()
                    tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                    tr.set_text(str(row.Message))
                    tr.set_to_lang('en')
                    mtrans = tr.translate()
                    st.success("\"" + row.Message + "\""+"\nTranslation Attempt: "+"\"" + mtrans + "\"")
                st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)
            else:
                if detlan =='en':
                    st.error("\"" + row.Message + "\"")
                else:
                    tr = Translater()
                    tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                    tr.set_text(str(row.Message))
                    tr.set_to_lang('en')
                    mtrans = tr.translate()
                    st.error("\"" + row.Message + "\""+"\nTranslation Attempt: "+"\"" + mtrans + "\"")
                st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)
