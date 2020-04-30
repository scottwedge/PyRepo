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
from datetime import datetime, timedelta
import pytz
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

def main():
    stask():
        print('Task fired')
    sched = BlockingScheduler()
    sched.add_job(stask,'interval', minutes=1)
    sched.start()

if __name__ == "__main__":
    main()
