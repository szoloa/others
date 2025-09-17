import json
from bs4 import BeautifulSoup as soup
from Problem import Problems

import pathlib
import os
import re

def fun(content, capter, TYPE, bankid):
    p = Problems('ask.db')

    for i in content['data']['questions']:
        stem = soup(i['stem'], 'lxml').text
        options = str([soup(i, 'lxml').text.replace('\n','') for i in i['options']])
        answer = str(i['answer'][0]) if i['answer'] else None
        analysis = str(soup(i['analysis'],'lxml'))
        p.addProblem(stem=stem, options=options, answer=answer, analysis=analysis, TYPE=TYPE, capter=capter, bankid=bankid)

    p.close()

path = '细胞生物学'

for root, dirs, files in os.walk(path):
    for name in files:
        capter = re.findall("第(.*?)章",os.path.join(root, name))
        capter = capter[0] if capter != [] else 0
        print(capter)
        TYPE = name.split('-')[-1].split('.')[0]
        with open(os.path.join(root, name),'r',encoding='utf-8') as f:
            content = json.load(f)
        fun(content=content, capter=capter, TYPE=TYPE, bankid=5)
