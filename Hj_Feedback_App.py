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
from datetime import datetime, timedelta
import pytz

def main():
    # options
    pd.set_option("display.precision", 3)
    pd.options.display.float_format = '{:.4f}'.format
    np.set_printoptions(precision=4, suppress=True)

    dlurl= 'https://insights.hotjar.com/api/v1/sites/1547206/feedback/256010/responses?fields=browser,content,created_datetime_string,created_epoch_time,country_code,country_name,device,id,index,os,response_url,short_visitor_uuid,window_size&sort=-id&offset=0&amount=30000&format=csv&filter=created__ge__2009-05-11'
    head2 = {
        'authority': 'insights.hotjar.com',
        'method': 'GET',
        'path': '/api/v1/sites/1547206/feedback/256010/responses?fields=browser,content,created_datetime_string,created_epoch_time,country_code,country_name,device,id,index,os,response_url,short_visitor_uuid,window_size&sort=-id&offset=0&amount=30000&format=csv&filter=created__ge__2020-03-24',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.2.408059203.1582125822; _gcl_au=1.1.2121588707.1582125822; _hjid=bcbc175b-2df6-400c-9358-65e7f264f87c; _BEAMER_USER_ID_zeKLgqli17986=dcee6938-859e-4348-bd34-f80d53c958b6; _BEAMER_FIRST_VISIT_zeKLgqli17986=2020-02-19T15:23:42.738Z; hubspotutk=c0b18dd390c94a77301d5605b29e6460; _fbp=fb.1.1582125894901.66546557; __zlcmid=wqivZyfBgbR6w5; _gcl_aw=GCL.1585228516.EAIaIQobChMI4N_Cspy46AIVGWyGCh09Mw6hEAAYASAAEgJOoPD_BwE; _gac_UA-51401671-1=1.1585228516.EAIaIQobChMI4N_Cspy46AIVGWyGCh09Mw6hEAAYASAAEgJOoPD_BwE; _hjDonePolls=481939,481419,156128,491599; _hjMinimizedPolls=481906,156128,491599; __hstc=162211107.c0b18dd390c94a77301d5605b29e6460.1582125822938.1585924808327.1586054543411.39; _BEAMER_DATE_zeKLgqli17986=2020-04-23T15:14:50.954Z; _hjIncludedInSample=1; _BEAMER_LAST_POST_SHOWN_zeKLgqli17986=1138945; _hjUserAttributesHash=ee9ffb91a314801cef0a410822bd5c93; receptiveNotificationCount=6; _gid=GA1.2.1421648835.1588522759; _BEAMER_FILTER_BY_URL_zeKLgqli17986=false; ajs_group_id=null; ajs_anonymous_id=%22370d38b8-df25-458d-98f3-bc48522865a6%22; SESSION-ID=5d56187f30230242e8df80fe3999d873f076ae2cb9154d4324dc6616; LOGGED-IN=1; XSRF-TOKEN=8ee15de54e4697ed2d70b246ab26123cefaaf59680fb57b5dcc0fbf2; ajs_user_id=1542301; _BEAMER_LAST_UPDATE_zeKLgqli17986=1588522765334; intercom-session-c5ke8zbr=ZWtxUm5MamgyVmNBWkRLbWFiZjBsazB3ZlNlN3FPLzJkODV0MUJjZ0dtTnJzTGhaZDhLSlpxR29ydUgxZXBlSS0tRCtvQmM3ekdGN3g2bFBrUDdPYjVldz09--b196cb6b8f9eb112cab13623a0d4cf21543ac32d; _uetsid=_ueta9119d5e-3277-b232-d1de-e2ac3853d822; _dd_s=rum=0&expire=1588524188050',
        'referer': 'https://insights.hotjar.com/sites/1547206/feedback/responses/256010',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
        }

    st.title("HotJar Feedback Analysis")

    timzo = pytz.timezone('US/Eastern')
    lastmod = os.path.getmtime('feedback-256010.csv')
    lastmod = datetime.fromtimestamp(lastmod)
    lastmodstr = lastmod.strftime('%m/%d/%Y'+' '+'%X')
    today = datetime.now()
    today = timzo.localize(today)
    lastmodloc = timzo.localize(lastmod)

    if st.button('Download latest HotJar data'):
        timzo = pytz.timezone('US/Eastern')
        lastmod = os.path.getmtime('feedback-256010.csv')
        lastmod = datetime.fromtimestamp(lastmod)
        lastmodstr = lastmod.strftime('%m/%d/%Y'+' '+'%X')
        today = datetime.now()
        today = timzo.localize(today)
        lastmodloc = timzo.localize(lastmod)
        if (today - timedelta(minutes=5)) >=lastmodloc:
            with requests.Session() as session:
                r = session.get(dlurl, headers=head2)
                #print(r.encoding)
                #r.text
                #print(r.text)
                with open('feedback-256010.csv', 'wb') as fd:
                    fd.write(r.content)
            dlresp = st.text('Download successful.')
        else:
            dlresp = st.text('Please wait 5 minutes before downloading again.')

    st.text('Showing data from Hotjar as of: '+str(lastmodstr))
    if lastmod.date() < today.date():
        st.error('Warning: we have detected that the feedback data is not up to date. Please hit "Download latest HotJar data" to fetch latest feedback.')
    elif lastmod.date() == today.date():
        st.info("Hotjar feedback data has been downloaded recently.")
    df = pd.read_csv('feedback-256010.csv')

    kvp = {"[All Feedback]" : "","Allen-Bradley" : "ab.rockwellautomation", "Rockwell Automation" : "www.rockwellautomation.com","RA/my" : "www.rockwellautomation.com/my","PCDC" : "compatibility.rockwellautomation",
    "Account" : "www.rockwellautomation.com/account/","Download.RA" : "download.rockwellautomation.com","Search" : "rockwellautomation.com/search","Investor Relations" : "ir.rockwellautomation",
    "Campaign Pages" : "campaign.rockwellautomation", "E-learning Pages" : "training/e-learning"}
    #cskvp = {"[No filter]":"", "English - NA":"en_NA", "Spanish - Central America":"es_CEM", "English - Caribbean":"en_CAR", "Spanish - Caribbean":"es_CAR", "English - Middle East":"en_MDE",
    #"English - Sub-Saharan Africa":"en_ZA", "English - Southeast Asia":"en_SEA", "Spanish - Argentina":"es_AR", "Spanish - Mexico":"es_MX", "Portuguese - Brazil":"pt_BR", "Chinese - China":"zh_CN",
    #"German - Germany":"de_DE", "Czech - Czech":"cs_CZ", "Spanish - Spain":"es_ES", "French - France":"fr_FR", "English - India":"en_IN", "English - Israel":"en_IL", "Italian - Italy":"it_IT",
    #"Japanese - Japan":"ja_JP","Korean - Korea":"ko_KR","Turkish - Turkey":"tr_TR", "English - United Kingdom":"en_GB", "Russian - Russia":"ru_RU"}
    ablkvp = {"[No language specified]":"","zh":"/zh/","Deutsch":"/de/","Spanish":"/es/","French":"/fr/","Italian":"/it/","Japanese":"/ja/","Korean":"/ko/","Portuguese":"/pt/"}
    tlkeys = {"[No country filter]":1,"NA":2,"EMEA":3,"APAC":4,"LAR":5}
    testlist = {1 : [""], 2 : ["en_NA"], 3 : ["cs_CZ","en_UK","nl_BE","da_DK","en_ZA","nl_NL","de_AT","es_ES","pl_PL","de_CH","fr_BE","pt_pt","de_DE","fr_CH","ru_RU","en_IE","fr_FR","sv_SE","en_IL","it_IT","tr_TR","en_MDE"],
    4 : ["zh_CN","ja_JP","zh_TW","en_SEA","ko_KR","en_AU","en_NZ","en_IN"], 5 : ["en_CAR","es_CL","es_PE","es_CAR","es_CO","es_VE","es_AR","es_EC","pt_BR","es_CEM","es_MX"]}
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
        down_df = down_df[down_df['Source URL'].str.contains('|'.join(testlist[tlindex]))]
    elif url == "ab.rockwellautomation":
        cssel = st.selectbox("Choose a region:", options=list(ablkvp.keys()))
        csfil = ablkvp[cssel]
        down_df = down_df[down_df['Source URL'].str.contains(csfil)]
    elif url == "rockwellautomation.com/search":
        down_df = down_df[down_df['Source URL'].str.contains('|'.join(["rockwellautomation.com/my/search",url]))]

    tmrange = st.number_input("Week range:", min_value=1,max_value=52,step=1)
    week_prior = today - timedelta(weeks=tmrange)

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
        st.write("Legend guide: Emotion 1 = Hate ... Emotion 5 = Love")
        histfig = px.histogram(date_df, x='Date Submitted', color='Emotion (1-5)',
            title='Feedback for URL over '+str(tmrange)+' week(s)',
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
        st.header('Pages of interest: these specific pages have recieve a high volume of negative feedbacks')
        st.write('Bubble size reflects total feedbacks for a specific page, bubble redness reflects amount of bad feedback for same page.')
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
            st.write('Links to worst performing pages (pulled from above):')
            for i in nlarg_df.itertuples():
                c = c+1
                st.write(str(c)+'. '+str(i._5))
        else:
            st.write("No pages of interest for given filters.")



    #pieplot = px.pie(down_df, names="Country", hole = .4, title="All Time Feedback Breakdown by country for "+url)
    #st.plotly_chart(pieplot)

    mess_df=date_df.loc[date_df["Message"].notna()]
    mess_df = mess_df.drop(columns=['Number',"User","OS"])

    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    if mess_df.empty == False:
        st.header("WordCloud for feedback responses:")
        cust_swords = ["Rockwell", "Automation"] + list(STOPWORDS)
        wcloud = WordCloud(background_color="white", scale=2, min_font_size=12,max_words=100,stopwords=cust_swords).generate(" ".join(mess_df['Message']))
        plt.figure(figsize=(20,10))
        plt.imshow(wcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        st.pyplot()
    else:
        st.write("No responses for given filters.")

    mfildic = {"[No filter]" : 1, "People who can't find a product" : 2, "People who can't download software" : 3, "People who may require a response" : 4, "E-learning or training issues" : 5}
    cfildic = {"[All Countries]" : 1, "United States" : 2, "Mexico" : 3, "China" : 4, "United Kingdom" : 5}
    kw1 = {1 : [""], 2 : ["find","where","part","no"], 3 : ["cant","can't","looking","find","issues","problem","downloading","how","nothing","impossible"], 4 : ["who","where","what","how"], 5 : [""]}
    kw2 = {1 : [""], 2 : ["part","product"], 3 : ["download", "downloading", "software"], 4 : ["?"], 5 : ["training", "elearning","e-learning","enrol"]}
    ckw = {1 : "", 2 : "United States", 3 : "Mexico", 4 : "China", 5 : "Mexico"}

    body="Here is a list of responses over the past "+str(tmrange)+" weeks for "+str(url)

    from yandex.Translater import Translater
    from langdetect import detect

    st.subheader('Responses over the past '+str(tmrange)+' week(s):')
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
                        try:
                            tr.set_from_lang(detlan)
                        except:
                            tr.set_from_lang('en')
                        tr.set_to_lang('en')
                        try:
                            mtrans = tr.translate(timeout=1)
                        except:
                            mtrans = '[Failed]'
                        st.info("\"" + row.Message + "\""+"  \nTranslation Attempt: "+"\"" + mtrans + "\"")
                    st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                    body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)
                elif row._7 >3:
                    if detlan == 'en':
                        st.success("\"" + row.Message + "\"")
                    else:
                        tr = Translater()
                        tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                        tr.set_text(str(row.Message))
                        try:
                            tr.set_from_lang(detlan)
                        except:
                            tr.set_from_lang('en')
                        tr.set_to_lang('en')
                        try:
                            mtrans = tr.translate(timeout=1)
                        except:
                            mtrans = '[Failed]'
                        st.success("\"" + row.Message + "\""+"  \nTranslation Attempt: "+"\"" + mtrans + "\"")
                    st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                    body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)
                else:
                    if detlan =='en':
                        st.error("\"" + row.Message + "\"")
                    else:
                        tr = Translater()
                        tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                        tr.set_text(str(row.Message))
                        try:
                            tr.set_from_lang(detlan)
                        except:
                            tr.set_from_lang('en')
                        tr.set_to_lang('en')
                        try:
                            mtrans = tr.translate(timeout=1)
                        except:
                            mtrans = '[Failed]'
                        st.error("\"" + row.Message + "\""+"  \nTranslation Attempt: "+"\"" + mtrans + "\"")
                    st.write("\- from **"+str(row.Email)+"** on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device), row._3)
                    body = body + '\n\n\"' + str(row.Message) + '\"' + '\n' + "- from "+str(row.Email)+" on "+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Browser)+" on "+str(row.Device)+'\n'+str(row._3)

if __name__ == "__main__":
    main()
