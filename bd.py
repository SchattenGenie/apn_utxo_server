#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redis import Redis
import mongoengine
from mongoengine import Document, IntField, StringField, EmbeddedDocumentField, FloatField, ListField, EmbeddedDocument
import json

mongoengine.connect()
redis = Redis()

class Wallet(Document):
    address = StringField(required=True)
    device_token = StringField(required=True)
    
    
class UTOX(EmbeddedDocument):
    tx_hash = StringField(required=True)
    script = StringField(required=True)
    value = FloatField(required=True)
    vout = IntField(required=True)
    confirmations = IntField(required=True)
    
class AddressUTOX(Document):
    address = StringField(required=True)
    UTOX = ListField(EmbeddedDocumentField(UTOX))
    

def get_wallets_from_db():
    # wallets = redis.get('wallets')
    # wallets = json.loads(wallets) if wallets is not None else []
    return Wallet.objects


def add_wallet_to_db(wallet):
    wallet = Wallet(address=wallet['address'], device_token=wallet['device_token'])
    wallet.save()
    return wallet