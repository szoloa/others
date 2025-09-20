from api_key import *
import requests
import Question
from bs4 import BeautifulSoup as soup
import re
import json

def ocr(url_):
        
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=" + get_access_token()
    
    payload=f'url={url_}&detect_direction=false&detect_language=false&paragraph=false&probability=false'
    headers = {
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
    
    return response.text
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    # q = Question.Questions()
    # for i in q.get_all_questions():
    #     if re.match('<html><body><p><img alt="" border="0" src=".*?"/></p>\n</body></html>', i['analysis']) and soup(i['analysis'], 'lxml').text == '\n':
    #         print(soup(i['analysis'], 'lxml').p.img.get('src'))
    #         # result = ocr(soup(i['analysis'], 'lxml').p.img.get('src'))
    #         # j_result = json.loads(result)
    #             # ress = ''.join([i['words'] for i in j_result['words_result']])
    #         q.update_question(id=i['id'], analysis=f"{soup(i['analysis'], 'lxml').p.img.get('src')}")
    #             # print(ress)
    q = Question.Questions()
    for i in q.get_all_questions():
        if i['answer']:
            if 'src' not in i['answer'] and '<p>' in i['answer']:
                # print(soup(i['analysis'], 'lxml').p.img.get('src'))
                print(soup(i['answer'], 'lxml').text)
                # result = ocr(soup(i['analysis'], 'lxml').p.img.get('src'))
                # j_result = json.loads(result)
                # ress = ''.join([i['words'] for i in j_result['words_result']])
                q.update_question(id=i['id'], analysis=f"{ress}")
                # print(ress)
        