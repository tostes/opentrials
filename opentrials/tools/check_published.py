#!/usr/bin/env python3

import sys
from http.client import HTTPConnection

SERVER = 'www.ensaiosclinicos.gov.br'
PATH = '/rg/%s/'

with open(sys.argv[1], 'r', encoding='utf-8') as id_file:
    for i, trial_id in enumerate(id_file, start=1):
        trial_id = trial_id.strip()
        if not trial_id:
            continue
        print('*' * 50, i, trial_id)
        connection = HTTPConnection(SERVER)
        try:
            connection.request('GET', PATH % trial_id)
            response = connection.getresponse()
            print(response.status, response.reason)
        finally:
            connection.close()

