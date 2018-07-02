import sys
import os
sys.path.append(os.path.abspath('../tracker'))
import tracker_bot as tbot
import pandas as pd

from flask import Flask, render_template

import json
import logging
from datetime import datetime
from anytree import NodeMixin, RenderTree, AsciiStyle

class BotNode(NodeMixin):
    name = None
    nick = None
    host = None
    vpn = None
    exitnode = None

    def __init__(self, nick, parent=None):
        self.nick = nick
        self.parent = parent

logging.basicConfig(format="%(threadName)s:%(message)s", level='NOTSET')

app = Flask(__name__)

# ==============================================================================
# Initial static data parsing from file
# ==============================================================================
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
    'matchmakers' : 'peers',
}

u_nicks = data.nick.unique().tolist()

# main data storage for graph
u_nicks_data = {}
for n in u_nicks:
    u_nicks_data[n] = {}
    for k in units.keys():
        dt = data.loc[(data['nick']==n) & (data['type']==k)]
        df = dt.filter(items=['timestamp', 'value'])
        df.columns=['x', 'y']
        df.x = df.x.astype(str)
        u_nicks_data[n][k] = df.to_dict('records')


nodes = [{'id': n, 'label': n, 'group':u_nicks.index(n)} for n in u_nicks]
edges = []

_data_network = {'nodes':nodes, 'edges': edges}

# ==============================================================================
# Dynamic data parsing
# new data is stored in memory as tree
# ==============================================================================
bot_info_keys = ['host', 'exitnode', 'tree', 'vpn']
bot_info_buffer = []
bot_nodes = []

def handle_data(bot_nick, key, value):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
   
    bot = BotNode(bot_nick)

    if bot not in bot_nodes:
        bot_nodes.append(bot)

    if key == 'host':
        bot.host = value
    elif key == 'exitnode':
        bot.exitnode = value
    elif key == 'tree':
        bot.tree = value
    elif key == 'vpn':
        bot.vpn = value
    else:
        if bot_nick not in u_nicks_data.keys():
            u_nicks_data[bot_nick] = {}

        if key not in u_nicks_data[bot_nick].keys():
            u_nicks_data[bot_nick][key] = []
        
        u_nicks_data[bot_nick][key].append({'x': current_time, 'y': value})

    for pre, _, node in RenderTree(bot):
        treestr = u"%s%s" % (pre, node.nick)
        logging.info(treestr.ljust(8))

tracker = tbot.TrackerBot('watcher', handle_data)

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
