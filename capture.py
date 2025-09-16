import requests
import json
from bs4 import BeautifulSoup as soup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2540621) XWEB/16203',
    'Referer':'https://s6-xunke.cdn.ixunke.cn/',
    'Origin': 'https://s6-xunke.cdn.ixunke.cn',
    'Sec-Fetch-Dest': 'empty'
}

#GET /yantikuaishua/api/v1/question/sequence_practise_nestification?app=true&token=&qBankId=44&chapterId=24753&studentAnswer=1 HTTP/1.1

url = 'https://api.ixunke.cn//yantikuaishua/api/v1/question/sequence_practise_nestification'
payload = {
    'app': 'true',
    'token':'VTJGc2RHVmtYMTkyOGxjY21hSE94ZjNRVUpiMlB0L055ZURiR0hOeGVrd0U5VStLYlo2TitJenVBY2tsck80NUtjdGJrd3ZEbnA4c3JDNHVQNnNPa1FZN2J3VEFkdVVPa3ZZWVJRRWxIQWc9IzE3NTgwMjQ5OTIwMzUtNTUzMQ%3D%3D',
    'qBankId':'44',
    'chapterId':'24755',
    'studentAnswer':'1'
}

r = requests.get(url=url, headers=headers, params=payload)

with open(f'c.txt', '+a', encoding='utf-8') as f:
    f.write(r.text)

# with open('a.txt','r',encoding='utf-8') as f:
#     content = json.load(f)

# for i in content['data']['questions']:
#     print(soup(i['stem'], 'lxml').text)
    