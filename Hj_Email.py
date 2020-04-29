import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import atexit

def main():

    dlurl= 'https://insights.hotjar.com/api/v1/sites/1547206/feedback/256010/responses?fields=browser,content,created_datetime_string,created_epoch_time,country_code,country_name,device,id,index,os,response_url,short_visitor_uuid,window_size&sort=-id&offset=0&amount=30000&format=csv&filter=created__ge__2009-05-11'
    head2 = {
    'authority': 'insights.hotjar.com',
    'method': 'GET',
    'path': '/api/v1/sites/1547206/feedback/256010/responses?fields=browser,content,created_datetime_string,created_epoch_time,country_code,country_name,device,id,index,os,response_url,short_visitor_uuid,window_size&sort=-id&offset=0&amount=30000&format=csv&filter=created__ge__2020-03-24',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_ga=GA1.2.408059203.1582125822; _gcl_au=1.1.2121588707.1582125822; _hjid=bcbc175b-2df6-400c-9358-65e7f264f87c; _BEAMER_USER_ID_zeKLgqli17986=dcee6938-859e-4348-bd34-f80d53c958b6; _BEAMER_FIRST_VISIT_zeKLgqli17986=2020-02-19T15:23:42.738Z; hubspotutk=c0b18dd390c94a77301d5605b29e6460; _fbp=fb.1.1582125894901.66546557; __zlcmid=wqivZyfBgbR6w5; _gaexp=GAX1.2.3nykdqqmSsichHKl_hW0Kg.18377.x411; _hjUserAttributesHash=0b86f28c0b60220a48ce656c996d5abb; _gcl_aw=GCL.1585228516.EAIaIQobChMI4N_Cspy46AIVGWyGCh09Mw6hEAAYASAAEgJOoPD_BwE; _gac_UA-51401671-1=1.1585228516.EAIaIQobChMI4N_Cspy46AIVGWyGCh09Mw6hEAAYASAAEgJOoPD_BwE; _hjDonePolls=481939,481419,156128,491599; _hjMinimizedPolls=481906,156128,491599; __hstc=162211107.c0b18dd390c94a77301d5605b29e6460.1582125822938.1585924808327.1586054543411.39; _hjCachedUserAttributes={"userId":1542301,"attributes":{"account_feature_flags":null,"became_a_customer":"2020-01-24T21:33:47.000Z","country":"US","highest_plan":"business","highest_sample_rate":120000,"referrer_url":"referral","signed_up":"2020-02-19T15:24:51.000Z","site_industry":"other","site_lowest_alexa_rank":29099,"user_role":"other"}}; _BEAMER_LAST_POST_SHOWN_zeKLgqli17986=null; _BEAMER_DATE_zeKLgqli17986=2020-04-23T15:14:50.954Z; _gid=GA1.2.1583578170.1587655734; receptiveNotificationCount=3; ajs_anonymous_id=%22734d76cb-26f4-4127-912f-5b506b19011f%22; ajs_group_id=null; SESSION-ID=386af0988f2e17885ae796cb62840147efe40196bcf919437997f1d9; LOGGED-IN=1; XSRF-TOKEN=164d4630833d6364a25ad5c90ca09bff2f4c152e149ffcc89850e3e5; _BEAMER_LAST_UPDATE_zeKLgqli17986=1587678397663; ajs_user_id=1542301; _uetsid=_uet4314a83f-3455-8651-033a-1a4e8faae7b0; receptivePingSent=true; _gat=1; intercom-session-c5ke8zbr=TjhDZk9mOXRiNExib1dkK3REVk5GYjhobStmL2pRdHpxMkJKd0h1dVBDbnN1bzdMaTg1L2FPRmdxRVdjTFJDei0tTzNYNTNjSnJvYnZpbW9ScUtHQ3VLUT09--3390ae62221112fc1128b0f0fd743436a13dd0c7; _dd_s=rum=1&id=866cee7b-518f-4cda-af15-f886fff3bb24&created=1587673344759&expire=1587680792039',
    'referer': 'https://insights.hotjar.com/sites/1547206/feedback/responses/256010',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
    }

    st.title("HotJar Automated Email Feedback")

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
    contdf = pd.read_csv('HJemail_contacts.csv')
    vis_df = contdf.set_index(['Site']).apply(lambda x: x.str.split(', ').explode()).reset_index()
    unique_emails = vis_df.Emails.unique()
    #last_monday= today - timedelta(days=today.weekday())
    #st.write(last_monday)
    if lastmod.date() < today.date():
        st.error("Warning: we have detected that the feedback data is not up to date. Please download the latest feedback CSV from HotJar and move to the appropriate location before sending any emails!")
    elif lastmod.date() == today.date():
        st.info("Hotjar feedback data has been downloaded and is up to date. Send away!")
    webdic = {"[All Feedback]" : "","Allen-Bradley" : "ab.rockwellautomation", "Rockwell Automation" : "www.rockwellautomation.com","RA/my" : "www.rockwellautomation.com/my","PCDC" : "compatibility.rockwellautomation",
    "Account" : "www.rockwellautomation.com/account/","Download.RA" : "download.rockwellautomation.com","Search" : "rockwellautomation.com/search","Investor Relations" : "ir.rockwellautomation",
    "Campaign Pages" : "campaign.rockwellautomation", "RA - NA" : "North America", " RA - EMEA" : "EMEA", " RA - APAC" : "APAC", "RA - LAR" : "LAR"}
    st.sidebar.header('Send Emails:')
    webms = st.sidebar.multiselect("Choose site feedback(s) to send:", list(webdic.keys()), key='testkey')
    etype=st.sidebar.selectbox("Email Type:",['Responses','Visualizations'])
    urlsld = []
    for site in webms:
        urlsld.append(webdic[site])
    tmrange = st.sidebar.number_input("Send data for past _ week(s):", min_value=1, max_value=52, step=1)
    target_email = st.sidebar.selectbox("Email recipients:", unique_emails)
    def schtask():
        sendEmail('olander.14@yahoo.com',"www.rockwellautomation.com",1,'Visualizations')
    #@st.cache()
    #def setupSch():
    sched = BlockingScheduler()
    sched.add_job(schtask,'interval', minutes=5, id='sendvisemails_test')
    sched.start()
    #setupSch()
    #atexit.register(lambda: sched.shutdown())
    if st.sidebar.button("Send email"):
        for url in urlsld:
            sendEmail(target_email,url,tmrange,etype)

    #contdf = pd.read_csv('HJemail_contacts.csv')
    edf = pd.read_csv('email_records.csv')
    edf['Date'] = pd.to_datetime(edf['Date'])
    contdf['Emails']=contdf['Emails'].str.split(', ')
    #contdf
    #edf
    for row in contdf.itertuples():
        site_edf=edf.loc[edf['URL']==row.Site]
        st.markdown('<hr>', unsafe_allow_html=True)
        st.header(str(row.Site))
        for e in row.Emails:
            em_edf=site_edf.loc[site_edf['Recipient']==e]
            st.subheader('Contact: '+str(e))
            visgood = 0
            respgood = 0
            v_em_edf=em_edf.loc[em_edf['Email_type']=='Visualizations']
            r_em_edf=em_edf.loc[em_edf['Email_type']=='Responses']
            if v_em_edf.empty == False:
                mostrecentv = v_em_edf['Date'].max()
                mrv_str = mostrecentv.strftime('%m/%d/%Y')
                if (today - timedelta(weeks=4)) > mostrecentv:
                    #It has been +4 weeks since last vis report.
                    st.markdown('<p>&#128314 Last visualization report sent on: <font color="red">'+mrv_str+'</font></p>',unsafe_allow_html=True)
                    #st.warning('Action Item: ')
                else:
                    st.markdown('<p>&#9989 Last visualization report sent on: <font color="green">'+mrv_str+'</font></p>',unsafe_allow_html=True)
            else:
                st.markdown('<p>&#128314 (Never been sent a visualization report)</p>',unsafe_allow_html=True)
                #st.warning('Action Item: ')
            if r_em_edf.empty == False:
                mostrecentr = r_em_edf['Date'].max()
                mrr_str = mostrecentr.strftime('%m/%d/%Y')
                if (today - timedelta(weeks=1)) > mostrecentr:
                    #It has been +1 weeks since a response report
                    st.markdown('<p>&#128314 Last response report sent on: <font color="red">'+mrr_str+'</font></p>',unsafe_allow_html=True)
                    #st.warning('Action Item: ')
                else:
                    st.markdown('<p>&#9989 Last response report sent on: <font color="green">'+mrr_str+'</font></p>',unsafe_allow_html=True)
            else:
                st.markdown('<p>&#128314 (Never been sent a response report)</p>',unsafe_allow_html=True)
                #st.warning('Action Item: ')

def sendEmail(target_email,url,tmrange,etype):
    df = pd.read_csv('feedback-256010.csv')
    edf = pd.read_csv('email_records.csv')
    if url == "EMEA":
        csites = ["cs_CZ","en_UK","nl_BE","da_DK","en_ZA","nl_NL","de_AT","es_ES","pl_PL","de_CH","fr_BE","pt_pt","de_DE","fr_CH","ru_RU","en_IE","fr_FR","sv_SE","en_IL","it_IT","tr_TR","en_MDE"]
        down_df = df[df['Source URL'].str.contains('|'.join(csites))]
    elif url == "North America":
        csites = ["en_NA"]
        down_df = df[df['Source URL'].str.contains('|'.join(csites))]
    elif url == "APAC":
        csites = ["zh_CN","ja_JP","zh_TW","en_SEA","ko_KR","en_AU","en_NZ","en_IN"]
        down_df = df[df['Source URL'].str.contains('|'.join(csites))]
    elif url == "LAR":
        csites = ["en_CAR","es_CL","es_PE","es_CAR","es_CO"]
        down_df = df[df['Source URL'].str.contains('|'.join(csites))]
    elif url == "rockwellautomation.com/search":
        csites = ['rockwellautomation.com/search','rockwellautomation.com/my/search']
        down_df = df[df['Source URL'].str.contains('|'.join(csites))]
    else:
        down_df = df[df['Source URL'].str.contains(url)]

    today = datetime.now()
    timzo = pytz.timezone('US/Eastern')
    today = timzo.localize(today)
    week_prior = today - timedelta(weeks=tmrange)


    down_df['Date Submitted'] = pd.to_datetime(down_df['Date Submitted'])
    down_df['Date Submitted']=down_df['Date Submitted'].dt.tz_localize(tz='US/Eastern', nonexistent='shift_forward')
    date_df = down_df.loc[down_df['Date Submitted'] >= week_prior]

    if date_df.empty == True:
        st.write("No data for time given, email not sent for "+str(url))
        return

    testemail = MIMEMultipart()
    sender_email = "rsolander@gmail.com"
    pw = "Ao1HO2RO3"
    #target_email = "olander.14@yahoo.com"
    testemail["From"] = sender_email
    testemail["To"] = target_email
    testemail["Subject"] = "Hotjar feedback from "+week_prior.strftime("%m/%d")+" to "+ today.strftime("%m/%d")+" | "+str(url)

    if etype == 'Responses':
        mess_df=date_df.loc[date_df["Message"].notna()]
        mess_df = mess_df.drop(columns=['Number',"User","OS"])

        htmlbod = '<html><body><h1>Hotjar feedback over past '+str(tmrange)+' weeks for '+str(url)+'</h1>'
        if mess_df.empty == True:
            htmlbod = '<html><body><p>No feedback responses for '+str(url)+' over '+str(tmrange)+' week(s).</p>'
        #Emjois: 5: 128522,1F60A 4: 128527, 1F60F 3: 128528, 1F610 2: 128530 1F612 1: 128544, 1F620
        #Link : 128279, 1F517
        emo = '128528'

        from yandex.Translater import Translater
        from langdetect import detect

        for row in mess_df.itertuples():
            if str(row.Email)=="nan":
                email = '<b>(unknown)</b>'
            else:
                email = '<b>'+str(row.Email)+'</b>'
            if row._7==1:
                emo='128544'
            elif row._7==2:
                emo='128530'
            elif row._7==3:
                emo='128528'
            elif row._7==4:
                emo='128527'
            elif row._7==5:
                emo='128522'
            try:
                detlan = detect(str(row.Message))
            except:
                detlan = 'en'
            if detlan == 'en':
                htmlbod = htmlbod+'<p><q>'+str(row.Message)+'</q></p><p>&#'+emo+email+' on '+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device)+'</p><a href='+str(row._3)+'>&#128279'+str(row._3)+'</a><hr>'
            else:
                try:
                    tr = Translater()
                    tr.set_key('trnsl.1.1.20200326T171128Z.c6e42851517b0a0a.363c0f12f70ef655b2ea466b33e40856c53df6c8')
                    tr.set_text(str(row.Message))
                    tr.set_to_lang('en')
                    mtrans = tr.translate()
                except:
                    mtrans = "Translation failed."
                htmlbod = htmlbod+'<p><q>'+str(row.Message)+'</q></p><p>Translation attempt: <q>'+mtrans+'</q></p><p>&#'+emo+email+' on '+row._1.strftime("%m/%d/%Y, %H:%M:%S")+" | "+str(row.Country)+" | "+str(row.Browser)+" on "+str(row.Device)+'</p><a href='+str(row._3)+'>&#128279'+str(row._3)+'</a><hr>'

        htmlbod = htmlbod + '</body></html>'
        testemail.attach(MIMEText(htmlbod, "html"))

    if etype == 'Visualizations':
        histfig = px.histogram(date_df, x='Date Submitted', color='Emotion (1-5)',
                          title='Feedback Responses for '+str(url),
                          opacity=0.8,
                           category_orders={'Emotion (1-5)':[1,2,3,4,5]},
                           color_discrete_map={1:"#e83b3a",2:"#c97d7d",3:"#BAB0AC",4:"#99bd9c",5:"#4cba76"},
                           nbins=20
        )
        histfig.update_layout(xaxis_tickformat='%d %B (%a)', xaxis=dict(dtick=86400000.0))
        histfig.write_image('histfigtest.png')

        counfig = px.histogram(date_df, y='Country', color='Emotion (1-5)',
            title='Breakdown by Country for url given',
            opacity=0.8,
            orientation = 'h',
            height = 1000,
            category_orders={'Emotion (1-5)':[1,2,3,4,5]},
            color_discrete_map={1:"#e83b3a",2:"#c97d7d",3:"#BAB0AC",4:"#99bd9c",5:"#4cba76"},
            #nbins=20
        ).update_yaxes(categoryorder="total ascending")
        counfig.write_image('counfig.png')

        apdate_df=date_df
        apdate_df['feedback_count']= apdate_df['Source URL'].map(apdate_df['Source URL'].value_counts())
        bad_df = apdate_df.loc[(apdate_df['Emotion (1-5)'] == 1) | (apdate_df['Emotion (1-5)'] == 2)]
        intr_df = bad_df[bad_df.duplicated(subset='Source URL', keep=False)]
        bdap_df=intr_df
        bdap_df['negative_feedbacks']= bdap_df['Source URL'].map(bdap_df['Source URL'].value_counts())
        intrfig = px.scatter(bdap_df, title='Pages of interest (Which pages are getting lots of bad feedback?)', y='Source URL', x='negative_feedbacks', color='negative_feedbacks', text='feedback_count', color_continuous_scale=px.colors.sequential.YlOrRd, size='feedback_count')
        intrfig.update_layout(margin=dict(l=500,r=10,t=40,b=20),xaxis=dict(dtick=1))
        intrfig.layout.coloraxis.showscale = False
        dd_df = bdap_df.drop_duplicates(subset='Source URL', keep='first')
        nlarg_df = dd_df.nlargest(5,['negative_feedbacks'])

        with open('histfigtest.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='img1.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='img1.png')
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            testemail.attach(mime)
        with open('counfig.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='img2.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='img2.png')
            mime.add_header('X-Attachment-Id', '1')
            mime.add_header('Content-ID', '<1>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            testemail.attach(mime)
        with open('intrfig.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='img3.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='img3.png')
            mime.add_header('X-Attachment-Id', '2')
            mime.add_header('Content-ID', '<2>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            testemail.attach(mime)

        embimg = '<html><body><h1>HotJar Report</h1>'+'<p><img src="cid:0"></p>'+'<img src="cid:1"></p>'+'<img src="cid:2"></p>'+'</body></html>'
        testemail.attach(MIMEText(embimg, 'html','utf-8'))

    session = smtplib.SMTP('smtp.gmail.com', 587, None, 30)
    session.starttls()
    session.login(sender_email, pw)
    session.set_debuglevel(1)
    text = testemail.as_string()
    session.sendmail(sender_email, target_email, text)
    session.quit()

    rec_dict = {"Date":today, "Recipient":target_email, "URL":url, "Email_type":etype}
    nedf = pd.DataFrame(rec_dict, index=[0])
    upd_edf = edf.append(nedf, ignore_index = True)
    upd_edf.to_csv('email_records.csv', index = False)

    st.write("Email for "+str(url)+" sent to "+str(target_email))

if __name__ == "__main__":
    main()
