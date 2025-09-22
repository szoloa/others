try:
    from api_key import doubao_api_key
except:
    doubao_api_key = ''
import os

from volcenginesdkarkruntime import Ark

def ai(content):
    if not doubao_api_key:
        return '无法获取api_key'

    client = Ark(api_key=doubao_api_key)

    response = client.chat.completions.create(
        model="doubao-1-5-pro-32k-250115",
        messages=[{"content":"帮我分析这道题的解析，输出使用纯文本的格式，不要使用markdown格式，回答简短，尽量不要超过200字","role":"system"},{"content":content,"role":"user"}],
    )
    return dict(response.choices[0].message)['content']

if __name__ == '__main__':
    print(dict(ai(''))['content'])
