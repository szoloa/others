import json
from bs4 import BeautifulSoup as soup
from Problem import Problems

p = Problems('ask.db')


with open('a.txt','r',encoding='utf-8') as f:
    content = json.load(f)

for i in content['data']['questions']:
    stem = soup(i['stem'], 'lxml').text
    options = str([soup(i, 'lxml').text.replace('\n','') for i in i['options']])
    answer = i['answer'][0]
    analysis = str(soup(i['analysis'],'lxml'))
    p.addProblem(stem=stem, options=options, answer=answer, analysis=analysis, TYPE=1)

p.close()