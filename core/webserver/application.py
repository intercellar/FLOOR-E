#!/usr/bin/python -B

from flask import Flask, render_template, url_for, copy_current_request_context, request, json, Markup
from random import random
from time import sleep
from threading import Thread, Event

info = {'lid': None,
        'pcb': None,
        'acc': None
       }

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

@app.route('/getinfo')
def info_getter():
    global info
    return json.dumps(info)

@app.route('/store', methods=['GET'])
def store():
    global info

    lid = request.args.get('lid')
    pcb = request.args.get('pcb')
    acc = request.args.get('acc')

    info['lid'] = lid
    info['pcb'] = pcb
    info['acc'] = acc

    return json.dumps({'success': True}), 200, {'ContentType:':'application/json'}

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=80)
    except:
        pass

