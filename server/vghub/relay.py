'''
Created on 9 lug 2021

@author: adamou
'''
from itsdangerous.serializer import Serializer
from itsdangerous.exc import BadSignature, BadData

s = Serializer("secret-key")
decoded_payload = None

try:
    decoded_payload = s.loads('[1,2,3,4,5]')
    # This payload is decoded and safe
except BadSignature as e:
    if e.payload is not None:
        try:
            decoded_payload = s.load_payload(e.payload)
        except BadData:
            pass