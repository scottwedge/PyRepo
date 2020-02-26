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
df = pd.read_csv('C:/Users/rsolande/Downloads/feedback-256010.csv')

sitelist = ["ab.rockwellautomation","www.rockwellautomation.com","www.rockwellautomation.com/my",
"compatibility.rockwellautomation","www.rockwellautomation.com/account/","download.rockwellautomation.com"]
url = st.selectbox("Choose a URL to analyze:",sitelist)
#URLs to consider:
#"ab.rockwellautomation"
#"www.rockwellautomation.com"
#"www.rockwellautomation.com/my"
#"compatibility.rockwellautomation"
#"www.rockwellautomation.com/account/"

down_df = df[df['Source URL'].str.contains(url)]

from datetime import datetime, timedelta

today = datetime.now()
week_prior = today - timedelta(weeks=2)
week_prior

down_df['Date Submitted'] = pd.to_datetime(down_df['Date Submitted'])
down_df = down_df.loc[down_df['Date Submitted'] >= week_prior]
st.write(down_df)

histfig = px.histogram(down_df, x='Date Submitted', color='Emotion (1-5)',
                      title='Feedback Responses for '+url,
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

pieplot = px.pie(down_df, names="Country", hole = .4, title="Feedback breakdown by country")
st.plotly_chart(pieplot)

mess_df=down_df.loc[down_df["Message"].notna()]
mess_df = mess_df.drop(columns=['Number',"User","Device","OS","Browser"])

for row in mess_df.itertuples():
    if row._5 == 3:
        st.info("\"" + row.Message + "\"")
        st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
    elif row._5 >3:
        st.success("\"" + row.Message + "\"")
        st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
    else:
        st.error("\"" + row.Message + "\"")
        st.write("\- from **"+str(row.Email)+"** on "+str(row._1), row._3)
