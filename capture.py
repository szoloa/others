import requests
import json
from bs4 import BeautifulSoup as soup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2540621) XWEB/16203',
    'Referer':'https://s6-xunke.cdn.ixunke.cn/',
    'Origin': 'https://s6-xunke.cdn.ixunke.cn',
    'Sec-Fetch-Dest': 'empty'
}

#GET /yantikuaishua/api/v1/question/sequence_practise_nestification?app=true&token=&qBankId=44&chapterId=24753&studentAnswer=1 HTTP/1.1

# url = 'https://api.ixunke.cn//yantikuaishua/api/v1/question/sequence_practise_nestification'
# payload = {
#     'app': 'true',
#     'token':'VTJGc2RHVmtYMTkyOGxjY21hSE94ZjNRVUpiMlB0L055ZURiR0hOeGVrd0U5VStLYlo2TitJenVBY2tsck80NUtjdGJrd3ZEbnA4c3JDNHVQNnNPa1FZN2J3VEFkdVVPa3ZZWVJRRWxIQWc9IzE3NTgwMjQ5OTIwMzUtNTUzMQ%3D%3D',
#     'qBankId':'54',
#     'chapterId':'24755',
#     'studentAnswer':'1'
# }

# r = requests.get(url=url, headers=headers, params=payload)

# host = 'https://api.ixunke.cn/'

# url = '/yantikuaishua/api/v1/question/sequence_practise_nestification?app=true&token=VTJGc2RHVmtYMTlqQUNzbEhxWmJHcjlsQW5DTlVNNk0zYTJHa0NxMjZ1ZTBlTmZxL0d0L0YxZk9ZbEQ0YVowUlptWjhpdmtBRGdMUDE1L1pEbXAyc1BYd2NBcE9vS01xdDhOREVDaUpKRnM9IzE3NTgwODM4OTk4NzYtNTQ2&qBankId=54&chapterId=24620&studentAnswer=1'

# r = requests.get(f'{host}{url}', headers=headers)

# with open(f'选择题.txt', '+a', encoding='utf-8') as f:
#     f.write(r.text)
#     f.write('\n\n')

# with open('a.txt','r',encoding='utf-8') as f:
#     content = json.load(f)

# for i in content['data']['questions']:
#     print(soup(i['stem'], 'lxml').text)


# host = 'https://api.ixunke.cn/'

# url = '/yantikuaishua/api/chapter?qBankId=52&rewardedAd=1&app=true&token=VTJGc2RHVmtYMTllUmhFY3JORjVmbFd5cEszdGtobE9WVlZzNDh4dFVxdHZqd0w2aGlJU09YOVJrZW5ITVlRU0lTdDF1WHFjcGZySHpXUGZmTldXbHc9PSMxNzU4MDkyNDk3ODg4'

# r = requests.get(f'{host}{url}', headers=headers)

# with open(f'微生物学.txt', '+a', encoding='utf-8') as f:
#     f.write(r.text)
#     f.write('\n\n')

# exit()

url = 'https://api.ixunke.cn//yantikuaishua/api/v1/question/sequence_practise_nestification'
payload = {
    'app': 'true',
    'token':'VTJGc2RHVmtYMS82bDZ4dEVXbVJ1RGFrajFMb1ZQYVBXRHczd0lFUEFSa2xITDNONnE2K2x4dDFQNEFpSWFPTXpyQWZISFY4L1l2RnhuYWtjZjFJSHV4aDhjdUZjNkJ4VkJsaEhqNFArUFU9IzE3NTgwOTI2NDI3MDEtMjgy',
    'qBankId':'52',
    'chapterId':'24755',
    'studentAnswer':'1'
}

with open('微生物学.txt','r',encoding='utf-8') as f:
    content = json.load(f)

for i in content['data'][-8:]:
    # print(i)
    # print(i['id'])
    print(i['title'])
    payload['chapterId'] = i['id']
    r = requests.get(url=url, headers=headers, params=payload)
    with open(f'微生物学/{i['title']}.txt', '+a', encoding='utf-8') as f:
        f.write(r.text)
    time.sleep(0.5)
    # for j in i['children']:
    #     print(j['id'])
    #     print(j['title'])
    #     payload['chapterId'] = j['id']
    #     r = requests.get(url=url, headers=headers, params=payload)
    #     with open(f'微生物学/{i['title']}-{j['title']}.txt', '+a', encoding='utf-8') as f:
    #         f.write(r.text)
    #     time.sleep(0.5)
