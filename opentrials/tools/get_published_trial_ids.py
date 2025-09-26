#!/usr/bin/env python3

import re
from urllib.request import urlopen

BASE = 'http://www.ensaiosclinicos.gov.br/rg/?page='

re_link = re.compile(
    r'''<a href="http://www\.ensaiosclinicos\.gov\.br/rg/(RBR-.*?)/">\1</a>''')

re_current = re.compile(r'''<span class="current">\s*(\d+)\s*</span>''')

page = 1
trial_ids = []
while True:
    with urlopen(BASE + str(page)) as response:
        html = response.read().decode('utf-8')
    res = re_current.findall(html)
    if len(res) == 0:
        break
    assert len(res) == 1
    assert int(res[0]) == page
    res = re_link.findall(html)
    trial_ids.extend(res)
    page += 1
for t in trial_ids:
    print(t)


# em 2011-12-14 este script, bem como a inpeção visual da lista pública de 
# ensaios, revela 53 ensaios publicados, porém o scoreboard na página
# principal do site diz "There are 59 registered trials."

