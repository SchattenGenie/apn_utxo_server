#!/usr/bin/env python
# -*- coding: utf-8 -*-

# node with bitcore-node and insight-api
BASE_URL = 'https://test-insight.swap.online/insight-api/addrs/utxo'

# parameters of server
HOST='0.0.0.0'
PORT='5000'

# parameters of push updates
CERT_FILE='aps_dev_cert.pem'
KEY_FILE='aps_dev_key_decrypted.pem'
EXPIRY=60 * 60 # seconds
PRIORITY=10
SYNC_PERIOD=120 # seconds
ONLINE_SYNC_PERIOD=3 # seconds
# DEBUG=True
