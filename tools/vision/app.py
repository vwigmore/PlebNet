import sys
import os
sys.path.append(os.path.abspath('../tracker'))
import tracker_bot as tbot
import pandas as pd

from flask import Flask, render_template

import json

print tbot.log_file_path + '/' +tbot.log_data_name

app = Flask(__name__)

nodes = [{'id': 0, 'label': "0", 'group': 0},
        {'id': 1, 'label': "1", 'group': 0},
        {'id': 2, 'label': "2", 'group': 0},
        {'id': 3, 'label': "3", 'group': 1},
        {'id': 4, 'label': "4", 'group': 1},
        {'id': 5, 'label': "5", 'group': 1},
        {'id': 6, 'label': "6", 'group': 2},
        {'id': 7, 'label': "7", 'group': 2},
        {'id': 8, 'label': "8", 'group': 2},
        {'id': 9, 'label': "9", 'group': 3},
        {'id': 10, 'label': "10", 'group': 3},
        {'id': 11, 'label': "11", 'group': 3},
        {'id': 12, 'label': "12", 'group': 4},
        {'id': 13, 'label': "13", 'group': 4},
        {'id': 14, 'label': "fourteen", 'group': 4},
        {'id': 15, 'label': "15", 'group': 5},
        {'id': 16, 'label': "16", 'group': 5},
        {'id': 17, 'label': "17", 'group': 5},
        {'id': 18, 'label': "18", 'group': 6},
        {'id': 19, 'label': "19", 'group': 6},
        {'id': 20, 'label': "20", 'group': 6},
        {'id': 21, 'label': "21", 'group': 7},
        {'id': 22, 'label': "22", 'group': 7},
        {'id': 23, 'label': "23", 'group': 7},
        {'id': 24, 'label': "24", 'group': 8},
        {'id': 25, 'label': "25", 'group': 8},
        {'id': 26, 'label': "26", 'group': 8},
        {'id': 27, 'label': "27", 'group': 9},
        {'id': 28, 'label': "28", 'group': 9},
        {'id': 29, 'label': "29", 'group': 9}
    ]

edges = [{'from': 1, 'to': 0},
        {'from': 2, 'to': 0},
        {'from': 4, 'to': 3},
        {'from': 5, 'to': 4},
        {'from': 4, 'to': 0},
        {'from': 7, 'to': 6},
        {'from': 8, 'to': 7},
        {'from': 7, 'to': 0},
        {'from': 10, 'to': 9},
        {'from': 11, 'to': 10},
        {'from': 10, 'to': 4},
        {'from': 13, 'to': 12},
        {'from': 14, 'to': 13},
        {'from': 13, 'to': 0},
        {'from': 16, 'to': 15},
        {'from': 17, 'to': 15},
        {'from': 15, 'to': 10},
        {'from': 19, 'to': 18},
        {'from': 20, 'to': 19},
        {'from': 19, 'to': 4},
        {'from': 22, 'to': 21},
        {'from': 23, 'to': 22},
        {'from': 22, 'to': 13},
        {'from': 25, 'to': 24},
        {'from': 26, 'to': 25},
        {'from': 25, 'to': 7},
        {'from': 28, 'to': 27},
        {'from': 29, 'to': 28},
        {'from': 28, 'to': 0}
    ]

_data_network = {'nodes':nodes, 'edges': edges}

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
data = data.set_index('timestamp')
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

print u_nicks

print data

@app.route('/')
def root():
    return render_template('index.html', data={})

@app.route('/network')
def network():
    return json.dumps(_data_network)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
