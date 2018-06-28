import sys
import os
sys.path.append(os.path.abspath('../tracker'))
import tracker_bot as tbot
import pandas as pd

from flask import Flask, render_template

import json

print tbot.log_file_path + '/' +tbot.log_data_name

app = Flask(__name__)

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

#########################################
## more prepping                       ##
#########################################
u_nicks = data.nick.unique().tolist()

u_nicks_data = {}
for n in u_nicks:
    u_nicks_data[n] = {}
    for k in units.keys():
        print(n + "\t" + k)
        dt = data.loc[(data['nick']==n) & (data['type']==k)]
        df = dt.filter(items=['timestamp', 'value'])
        df.columns=['x', 'y']
        df.x = df.x.astype(str)
        u_nicks_data[n][k] = df.to_dict('records')

nodes = [{'id': n, 'label': n, 'group':u_nicks.index(n)} for n in u_nicks]
edges = []

_data_network = {'nodes':nodes, 'edges': edges}

@app.route('/')
def root():
    return render_template('index.html', data=units.keys())

@app.route('/network')
def network():
    return json.dumps(_data_network)

@app.route('/node/<id>/<type>')
def node(id, type):
    if type in units.keys():
        return json.dumps(u_nicks_data[id][type])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
