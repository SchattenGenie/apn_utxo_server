#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apns import APNs, Frame, Payload
from bd import get_wallets_from_db
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from tools import return_unspent_outputs, gen_hash_for_dict
from bd import redis
import config
import logging
import json
import time
import requests

def create_apn_service(cert_file, key_file):
    apns = APNs(cert_file=cert_file, enhanced=True,
                key_file=key_file, use_sandbox=True)
    return apns


def update_wallets_states(force_update=False):
    wallets = get_wallets_from_db()
    addresses = [wallet['address'] for wallet in wallets]
    address_to_device_token = {wallet['address']: wallet['device_token'] for wallet in wallets}
    device_token_to_address = {wallet['device_token']: wallet['address'] for wallet in wallets}
    addresses_unspent_outputs = return_unspent_outputs(addresses)
    frame = Frame()
    frame_empty = True
    expiry = time.time() + config.EXPIRY
    priority = config.PRIORITY
    for address, utxos in addresses_unspent_outputs.items():
        previous_state_of_address = redis.get(address)
        current_state_of_address = gen_hash_for_dict(utxos)
        print(address, previous_state_of_address, current_state_of_address)
        if force_update or (current_state_of_address != previous_state_of_address):
            print('Sending...')
            for unspent_output in addresses_unspent_outputs[address]:
                frame_empty = False
                payload = Payload(alert=None, 
                                  sound=None, 
                                  custom={'data': json.dumps(unspent_output)}, 
                                  badge=1, 
                                  content_available=not force_update)
                frame.add_item(token_hex=address_to_device_token[address], 
                               payload=payload, identifier=1, expiry=expiry, priority=priority)
        redis.set(address, current_state_of_address)

    if not frame_empty:
        try:
            config.apns.gateway_server.send_notification_multiple(frame)
        except requests.exceptions.SSLError as e:
            print(e)
            time.sleep(1)
            config.apns = create_apn_service(cert_file=config.CERT_FILE, key_file=config.KEY_FILE)
        

def start_background_push_notifications():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=partial(update_wallets_states, force_update=True), trigger='interval', minutes=config.SYNC_PERIOD)

    scheduler.add_job(func=partial(update_wallets_states, force_update=False), trigger='interval', seconds=config.ONLINE_SYNC_PERIOD)
    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.WARNING)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)
    scheduler.start()
    return scheduler