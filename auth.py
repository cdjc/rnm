#!/usr/bin/env python3

import requests
import json

base = 'https://api.rightnow.org/api/media/'

url_auth = base+'authenticate'

HEADERS = {'Content-type' : 'application/json; charset=utf-8',
           'Accept' : 'application/vnd.rnapi.v4+json'}

class RNM:

    Token = None

    def authenticate(self, user, pswd):
        reply = self.post(url_auth, {'username':user, 'password':pswd})
        return reply

    def post(self, url, params):
        '''
        Send dict request to RNM and return the reply
        :param url: url
        :param params: dictionary of params
        :return: dictionary of results
        '''
        js = json.dumps(params)
        reply = requests.post(url, js, headers = HEADERS)
        return json.loads(reply.content.decode())