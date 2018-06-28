import os
import pandas as pd
import datetime as dt
import random

import warnings
warnings.filterwarnings('ignore')

# inspiration for improvements can be found here:
# http://www.djmannion.net/psych_programming/data/inferential/inferential.html
# https://blog.modeanalytics.com/python-data-visualization-libraries/


#########################################
## Initialize the data                 ##
#########################################

data_path = "~/.config/"
data_name = "tracker.data"
data_file = os.path.join(data_path, data_name)
cols = ['timestamp', 'nick', 'type', 'value']
data = pd.read_csv(data_file,
                   skipinitialspace=True,
                   delimiter=';',
                   error_bad_lines=False,
                   names=cols,
                   parse_dates=[0])

# remove null values
data = data.dropna(subset=['value'])
data = data[pd.to_numeric(data['value'], errors='coerce').notnull()]
data.value = data.value.astype(float)
# set index col properly
# data = data.set_index('timestamp')
# restore faults
data.type[data.type == 'BM_balance'] = 'MB_balance'

units = {
    'MB_balance' : 'MBs',
    'downloaded' : 'MBs',
    'uploaded' : 'MBs',
    'matchmakers' : 'matchmakers'
}

dd = data.loc[(data['nick']=='plebbot6197') & (data['type'] == 'downloaded') ]
df = data.filter(items=['timestamp', 'value'])
df.columns = ['x', 'y']

df.x = df.x.astype(str)

print df.to_dict()
