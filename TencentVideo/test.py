import requests

url = 'https://dm.video.qq.com/barrage/segment/r0045mxxntl/t/v1/30000/60000'
url = 'https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/90000/120000'


# resp = requests.get(url)
# print(resp.json())

def get_danmu(url):
    resp = requests.get(url)
    barrage_list = resp.json()['barrage_list']
    content = []
    for danmu in barrage_list:
        print(danmu['content'])
        content.append(danmu['content'])
        # quit()
        # print(i['content'])
    return content
    # print(barrage_list['barrage_list'])


i = 1
while True:
    num = 30000 * i
    url = f'https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/{num - 30000}/{num}'
    content = get_danmu(url)
    if not content:
        break
    i += 1
if __name__ == '__main__':
    pass
    # get_danmu(url)
