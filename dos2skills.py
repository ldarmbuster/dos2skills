#!/usr/bin/env python

import json
from bs4 import BeautifulSoup
import requests
import requests_cache
import re
from collections import OrderedDict
import unicodecsv as csv
import unicodedata

requests_cache.install_cache()

school_list = [
    'http://divinityoriginalsin2.wiki.fextralife.com/Aerotheurge+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Geomancer+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Huntsman+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Hydrosophist+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Necromancer+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Polymorph+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Pyrokinetic+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Scoundrel+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Summoning+Skills',
    'http://divinityoriginalsin2.wiki.fextralife.com/Warfare+Skills',
]

def pp(o):
    print json.dumps(o, indent=2)

def get_url(path):
    if path.startswith('http'):
        url = path
    else:
        url = 'http://divinityoriginalsin2.wiki.fextralife.com/{0}'.format(path.lstrip('/'))
    return url

def get_soup(where):
    if where.startswith('http'):
        url = where
    else:
        url = get_url(where)
    req = requests.get(url)
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def main():

    rows = []

    for school_url in school_list:
        sp = get_soup(school_url)
        cells = [i for i in sp.find('table', class_='wiki_table').find('tbody').find_all(re.compile(r'td|th'))]
        chunks = [cells[i:i + 10] for i in xrange(0, len(cells), 10)]

        for chunk in chunks:
            spell = OrderedDict()

            spell['Spell']  = chunk[0].text.strip()
            spell['Description'] = chunk[1].text.strip()

            reqs = re.findall(r'\d', chunk[2].text)
            spell['Hybrid'] = 'N'
            spell['Type1'] = re.search(r'(\w+)-skill', chunk[2].find_all('img')[0].get('src')).group(1).title()
            spell['Req1'] = reqs[0]
            if len(reqs) > 1:
                spell['Hybrid'] = 'Y'
                spell['Type2'] = re.search(r'(\w+)-skill', chunk[2].find_all('img')[1].get('src')).group(1).title()
                spell['Req2'] = reqs[1]
            else:
                spell['Type2'] = ''
                spell['Req2'] = ''

            spell['Mem'] = chunk[3].text.strip()

            if not chunk[4].find('img'):
                spell['AP'] = '0'
            else:
                ap = re.search(r'AP(\d?)\.png', chunk[4].find('img').get('src')).group(1)
                if not ap:
                    spell['AP'] = '1'
                else:
                    spell['AP'] = ap

            if not chunk[5].find('img'):
                spell['SP'] = '0'
            else:
                sp = re.search(r'SP(\d?)\.png', chunk[5].find('img').get('src')).group(1)
                if not sp:
                    spell['SP'] = '1'
                else:
                    spell['SP'] = sp

            spell['CD'] = chunk[6].text.strip()

            if not chunk[7].find('img'):
                spell['Res'] = chunk[7].text.strip()
            else:
                spell['Res'] = chunk[7].find('img').get('src').split('/')[-1][:3].upper()

            spell['Scale'] = chunk[8].text.strip()

            spell['Effect'] = chunk[9].text.strip()

            for k, v in spell.items():
                spell[k] = str(unicodedata.normalize('NFKD', unicode(v)))

            pp(spell)
            rows.append(spell)



    keys = rows[0].keys()
    with open('spells.csv', 'wb') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)

if __name__ == '__main__':
    main()
