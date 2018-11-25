#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from bd import redis, add_wallet_to_db
from pusher import create_apn_service, start_background_push_notifications
from flask import Flask, jsonify
from flask import request as frequest
import json

app = Flask(__name__)

@app.route('/subscribe', methods=['POST'])
def route_server():
    wallet_raw = json.loads(frequest.data)
    wallet = {}
    try:
        wallet['address'] = wallet_raw['address']
        wallet['device_token'] = wallet_raw['deviceToken']
    except KeyError:
        pass
    
    add_wallet_to_db(wallet)
    return 'true'

def main():
    config.apns = create_apn_service(cert_file=config.CERT_FILE, key_file=config.KEY_FILE)
    start_background_push_notifications()
    app.run(host=config.HOST, port=config.PORT)

if __name__ == "__main__":
    main()