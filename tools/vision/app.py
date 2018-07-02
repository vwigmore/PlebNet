import sys
import os
sys.path.append(os.path.abspath('../tracker'))
import tracker_bot as tbot
import pandas as pd

from flask import Flask, render_template

import json
import logging
from datetime import datetime

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

class BotNode(object):
    children = {}

    def __init__(self, id, index=''):
        self.id = id
        self.index = index
        self.dead = True

        self.nick = None
        self.host = None 
        self.exitnode = None
        self.vpn = None

    def set_status(self, nickname, host, exitnode, vpn):
        self.nick = nickname
        self.host = host 
        self.exitnode = (exitnode == 'True')
        self.vpn = (vpn == 'True')
        self.dead = False

    def alive(self):
        return not self.dead

    def get_child(self, id):
        if '.' in id:
            ch = id.split('.')
            ch_id = ch.pop(0)
            if self.index == '': # root
                ch_id = ch.pop(0) # child id                
            return self.children[ch_id].get_child('.'.join(ch))
        else:
            if len(id) == 1:
                ch_id = ch[0]
                return self.children[ch_id]
            else:
                raise ValueError("get_child: invalid id")

    def add_child(self, tree, id=''):
        if '.' in tree:
            ch = tree.split('.')
            ch_id = ch.pop(0)
            ident = id + '.' + ch_id
            if self.index == '': # root
                ch_id = ch.pop(0) # child id    
                ident = ident + '.' + ch_id
                if ch_id not in self.children:
                    self.children[ch_id] = BotNode(ident, ch_id)
            return self.children[ch_id].add_child('.'.join(ch), ident)
        else:
            if len(tree) == 1:
                ch_id = ch[0]
                ident = id + '.' + ch_id
                if ch_id not in self.children:
                    self.children[ch_id] = BotNode(ident, ch_id)
                return True
            else:
                raise ValueError("add_child: invalid id")        

    def create_edges(self):
        return


bot_info_keys = ['host', 'exitnode', 'tree', 'vpn']
bot_info_buffer = []
bot_nodes = {} #id=tree, bot

def handle_data(bot_nick, key, value):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
   
    if key == 'general':
        value = ' '.join(value)
        jd = value.replace("u\'", "\'").replace("True", "\'True\'").replace("False", "\'False\'").replace("\'", "\"")
        d = json.loads(jd)
        tree = d['tree']
        if '.' not in tree:
            if bot_nick not in bot_nodes:
                bot = BotNode(bot_nick)
                bot_nodes[bot_nick] = bot      
            else:
                bot_nodes[bot_nick].set_status(bot_nick, d['host'], d['exitnode'], d['vpn'])
        else:        
            bot_nodes[current].add_child(ch)
    else:
        if bot_nick not in u_nicks_data.keys():
            u_nicks_data[bot_nick] = {}

        if key not in u_nicks_data[bot_nick].keys():
            u_nicks_data[bot_nick][key] = []
        
        u_nicks_data[bot_nick][key].append({'x': current_time, 'y': value})


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

@app.route('/shownodes')
def show_nodes():
    nodes = []
    for bot in bot_nodes.values():
        nodes.append({
            'nick': bot.nick,
            'id': bot.id,
            'index': bot.index,
            'children': bot.children
        })    
    return json.dumps(nodes)    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
