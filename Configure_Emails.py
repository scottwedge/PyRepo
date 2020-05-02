import numpy as np
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
from streamlit import caching
from datetime import datetime, timedelta
import pytz
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

def main():
    st.title('Configure HotJar Email Contacts')
    contdf = pd.read_csv('HJemail_contacts.csv')
    webdic = {"Allen-Bradley" : "ab.rockwellautomation", "Rockwell Automation" : "www.rockwellautomation.com","RA/my" : "www.rockwellautomation.com/my","PCDC" : "compatibility.rockwellautomation",
    "Account" : "www.rockwellautomation.com/account/","Download.RA" : "download.rockwellautomation.com","Search" : "rockwellautomation.com/search","Investor Relations" : "ir.rockwellautomation",
    "Campaign Pages" : "campaign.rockwellautomation", "RA - NA" : "North America", " RA - EMEA" : "EMEA", " RA - APAC" : "APAC", "RA - LAR" : "LAR"}
    webms = st.selectbox("Configure emails for site:", options = list(webdic.keys()))
    selsite = webdic[webms]
    addsel = st.text_input('Email to add:')
    if st.button('Add email'):
        contdf = pd.read_csv('HJemail_contacts.csv')
        selsite = webdic[webms]
        if contdf.loc[contdf['Site']==selsite, 'Emails'].dropna().empty == True:
            #st.write('Detected empty')
            contdf.loc[contdf['Site']==selsite, 'Emails'] = addsel
            contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].str.strip(', ')
            contdf.to_csv('HJemail_contacts.csv', index=False)
            contdf = pd.read_csv('HJemail_contacts.csv')
            selsite = webdic[webms]
        elif addsel in contdf.loc[contdf['Site']==selsite, 'Emails'].values[0]:
            st.error('That email is already listed for '+str(selsite))
        else:
            #st.write('new email')
            contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].astype(str)+', '+addsel
            contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].str.strip(', ')
            contdf.to_csv('HJemail_contacts.csv', index=False)
            contdf = pd.read_csv('HJemail_contacts.csv')
            selsite = webdic[webms]

    if contdf.loc[contdf['Site']==selsite, 'Emails'].dropna().empty:
        st.subheader("There are no emails currently assigned to get this site feedback.")
        esel =st.empty()
    else:
        sel_contdf = contdf.loc[contdf['Site']==selsite]
        sel_contdf['Emails']=sel_contdf['Emails'].str.split(', ')
        options=sel_contdf.loc[sel_contdf['Site']==selsite, 'Emails'].values[0]
        #st.write(options)
        esel = st.multiselect('Select emails to remove:',options=options)
        if st.button('Remove email(s)'):
            contdf = pd.read_csv('HJemail_contacts.csv')
            selsite = webdic[webms]
            for sem in esel:
                #st.write(sem)
                contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].astype(str)+', '
                contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].str.replace((str(sem)+', '),'', regex=False)
                contdf.loc[contdf['Site']==selsite, 'Emails'] = contdf.loc[contdf['Site']==selsite,'Emails'].str.rstrip(', ')
            contdf.to_csv('HJemail_contacts.csv', index=False)
            contdf = pd.read_csv('HJemail_contacts.csv')
            selsite = webdic[webms]
    #st.write(sel_contdf)
    if contdf.loc[contdf['Site']==selsite, 'Emails'].dropna().empty==False:
        sel_contdf = contdf.loc[contdf['Site']==selsite]
        sel_contdf['Emails']=sel_contdf['Emails'].str.split(', ')
        for row in sel_contdf.dropna().itertuples():
            st.subheader('Emails scheduled to recieve feedback for '+ str(webms)+':')
            for e in row.Emails:
                st.text(e)

if __name__ == "__main__":
    main()
