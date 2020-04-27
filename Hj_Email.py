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
from apscheduler.schedulers.background import BackgroundScheduler

def main():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file in fileList:
        print('Title: %s, ID: %s' % (file['title'], file['id']))
        if(file['title'] == "Hotjar Folder"):
            folderID = file['id']
    fileList = drive.ListFile({'q': "'1jj3WQkwr9ewOS7u6bLEqfMshLvRbesMB' in parents and trashed=false"}).GetList()
    for file in fileList:
        print('Title: %s, ID: %s' % (file['title'], file['id']))
        if(file['title'] == "feedback-256010.csv"):
            hjdataID = file['id']
            lastmod = file['modifiedDate']
        if(file['title'] == "HJemail_contacts.csv"):
            hjconsID = file['id']

    fileob1 = drive.CreateFile({'id':hjdataID})
    fileob1.GetContentFile("feedback-256010.csv")
    fileob2 = drive.CreateFile({'id':hjconsID})
    fileob2.GetContentFile("HJemail_contacts.csv")

    st.title("HotJar Automated Email Feedback")
    contdf = pd.read_csv('HJemail_contacts.csv')
    vis_df = contdf.set_index(['Site']).apply(lambda x: x.str.split(', ').explode()).reset_index()
    unique_emails = vis_df.Emails.unique()
    #lastmod = os.path.getmtime('feedback-256010.csv')
    #lastmod = datetime.fromtimestamp(lastmod)
    lastmod = datetime.strptime(lastmod,'%Y-%m-%dT%H:%M:%S.%fZ')
    lastmodstr = lastmod.strftime('%m/%d/%Y')
    today = datetime.now()
    timzo = pytz.timezone('US/Eastern')
    today = timzo.localize(today)
    #last_monday= today - timedelta(days=today.weekday())
    #st.write(last_monday)
    if lastmod.date() < today.date():
        st.error("Warning: we have detected that the feedback data is not up to date. Please download the latest feedback CSV from HotJar and move to the appropriate location before sending any emails!")
    elif lastmod.date() == today.date():
        st.info("Hotjar feedback data has been downloaded and is up to date. Send away!")
    st.write('Feedback CSV last downloaded from hotjar: '+str(lastmodstr))
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
    sched = BlockingScheduler(daemon=True)
    sched.add_job(schtask,'cron', minute=26, id='sendvisemails_test')
    sched.start()
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
