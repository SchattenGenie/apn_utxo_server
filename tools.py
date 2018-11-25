#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import hashlib
from schema import Schema, Use, Optional, Or
from collections import defaultdict
import time
import requests
import config

wallet_schema = Schema({
    'address': Or(str, unicode), 
    'device_token': Or(str, unicode)
})

wallets_schema = Schema([wallet_schema])

unspent_output_schema = Schema({
    'tx_hash': Or(str, unicode),
    'script': Or(str, unicode),
    'value': int,
    'vout': int,
    'confirmations': int
})

unspent_outputs_schema = Schema({
    'timestamp': int,
    'outputs': [unspent_output_schema]
})

def preprocess_output(output):
    output_processed = {
        'value': output['satoshis'],
        'tx_hash': output['txid'],
        'script': output['scriptPubKey'],
        'confirmations': output['confirmations'],
        'vout': output['vout']
    }
    unspent_output_schema.validate(output_processed)
    return output_processed

def return_unspent_outputs(addresses):
    # get data from blockchain
    if not len(addresses):
        return defaultdict(list)
    r = requests.post(config.BASE_URL, data={'addrs':','.join(addresses)})
    try:
        raw_unspent_outputs = r.json()
    except ValueError:
        return defaultdict(list)
    d = defaultdict(list)
    for raw_unspent_output in raw_unspent_outputs:
        d[raw_unspent_output['address']].append(preprocess_output(raw_unspent_output))    
    
    return d


def gen_hash_for_dict(d):
    return hashlib.sha1(json.dumps(d, sort_keys=True)).hexdigest()