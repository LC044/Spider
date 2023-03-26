import requests
import json

from wordcloud import WordCloud
import PIL.Image as image
import numpy as np
import jieba


def getVid():  # !获取所有视频的vid
    headers = {
        "cookie": "pgv_pvid=6766918384; tvfe_boss_uuid=8aabd9b75a8cf9e4; video_platform=2; video_guid=15fa8088c86ca82a; RK=tM9gYEP0dJ; ptcz=38a3eccf78b58f599f70a36c1661f18acd222285d622c216bb6049616f3413ee; luin=o0863909694; lskey=00010000596e1de133d5203ddd766d8050ee4591b6fcfa1ab8d505a90e3bcc3c7d4cbbcef236ee77fac99c50; o_cookie=863909694; ptui_loginuin=616347231; pgv_info=ssid=s3352981908; main_login=qq; vuserid=321471598; vusession=zKyNjJh6LMR8x2DCWBB8bQ..; login_time_init=1647866493; _video_qq_version=1.1; _video_qq_main_login=qq; _video_qq_appid=3000501; _video_qq_vuserid=321471598; _video_qq_vusession=zKyNjJh6LMR8x2DCWBB8bQ..; _video_qq_login_time_init=1647866493; video_omgid=15fa8088c86ca82a; vversion_name=8.2.95; next_refresh_time=6566; _video_qq_next_refresh_time=6566; login_time_last=2022-3-21 20:42:6; uid=393142431",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
        "referer": "https://v.qq.com/",
    }
    payload = {
        "has_cache": 1,
        "page_params": {
            "cid": "mzc00200acwia9w",
            "id_type": "1",
            "lid": "",
            "page_context": "",
            "page_id": "vsite_episode_list",
            "page_num": "",
            "page_size": "30",
            "page_type": "detail_operation",
            "req_from": "web",
            "vid": "g00423lkmas",
        }
    }
    url = 'https://pbaccess.video.qq.com/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=3000010&vplatform=2'
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()['data']['module_list_datas'][0]['module_datas'][0]['item_data_lists']['item_datas']
    vids = []
    titles = []
    for item in data:
        vid = item['item_params']['vid']
        title = item['item_params']['union_title']
        vids.append(vid)
        titles.append(title)
        # print(vid)
    # print(vids)
    return vids, titles


def get_targetID(cid):  # ! 获取targetID
    url = "https://access.video.qq.com/danmu_manage/regist?vappid=97767206&vsecret=c0bdcbae120669fff425d0ef853674614aa659c605a613a4&raw=1"
    payload = {"wRegistType": 2,
               "vecIdList": [cid],
               "wSpeSource": 0,
               "bIsGetUserCfg": 1,
               "mapExtData": {
                   cid: {
                       "strCid": "mzc00200acwia9w",
                       "strLid": ""
                   }
               }
               }
    resp = requests.post(url, json=payload)
    data = resp.json()['data']['stMap'][cid]['strDanMuKey']
    target_id = data.split('targetid=')[-1]
    # print(target_id)
    return target_id


def get_danmu(target_id, timestamp):  # ! 获取弹幕
    Payload = {
        "otype": "json",
        "callback": "jQuery19104233449465496275_1647866555917",
        "target_id": target_id,
        # 7712619175&vid=k0042f69enx
        "session_key": "0,745,1647867972",
        "timestamp": timestamp,
        "_": "1647866555922",
    }
    url = 'https://mfm.video.qq.com/danmu'
    resp = requests.get(url, data=Payload)
    # print(resp.text)
    data = resp.text.lstrip(Payload['callback'] + '(').rstrip(")")
    data = json.loads(data, strict=False)
    comments = data['comments']
    content = []
    for comment in comments:
        danmu = comment['content']
        content.append(danmu)
    # print(content)
    return content


def write_file(filename, content):  # ! 将内容写入文件
    with open(filename, 'a', encoding='utf-8') as f:
        for c in content:
            f.writelines(c + ';')
        f.write('\n\n')


def trans_CN(text):  # ! 中文分词
    # 接收分词的字符串
    word_list = jieba.cut(text)
    # 分词后在单独个体之间加上空格
    result = " ".join(word_list)
    return result


def wordCloud(file):  # ! 生成词云
    f = open(file, 'r', encoding='utf-8')
    text = f.read()
    f.close
    text = trans_CN(text)
    stopwords = set()
    content = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords.update(content)
    # fp = open('stopwords.txt','r',encoding='utf-8')
    # stopwords = fp.read()
    # fp.close
    # stopwords = set(stopwords.split('，'))
    # print(stopwords)
    # mask = np.array(image.open("F:\wordcloud\image\love.jpg"))
    wordcloud = WordCloud(
        # 添加遮罩层
        # mask=mask,
        # 生成中文字的字体,必须要加,不然看不到中文
        width=1600,
        height=1200,
        stopwords=stopwords,
        font_path="C:\Windows\Fonts\STXINGKA.TTF"
    ).generate(text)
    image_produce = wordcloud.to_image()
    filename = file.rstrip('.txt') + '.png'
    wordcloud.to_file(filename)


def wordCloud0(file):  # ! 生成词云
    f = open(file, 'r', encoding='utf-8')
    text = f.read()
    f.close
    return text


def wordCloud1(text):
    result = trans_CN(text)
    text = trans_CN(text)
    stopwords = set()
    content = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords.update(content)
    # fp = open('stopwords.txt','r',encoding='utf-8')
    # stopwords = fp.read()
    # fp.close
    # stopwords = set(stopwords.split('，'))
    # print(stopwords)
    # mask = np.array(image.open("F:\wordcloud\image\love.jpg"))
    wordcloud = WordCloud(
        # 添加遮罩层
        # mask=mask,
        # 生成中文字的字体,必须要加,不然看不到中文
        width=1600,
        height=1200,
        stopwords=stopwords,
        font_path="C:\Windows\Fonts\STXINGKA.TTF"
    ).generate(text)
    image_produce = wordcloud.to_image()
    # filename = file.rstrip('.txt')+'.png'
    wordcloud.to_file('1.png')


def main():
    vids, titles = getVid()
    target_ids = []
    for vid in vids:
        target_id = get_targetID(vid)
        target_ids.append(target_id)
    print(target_ids, titles)
    # filename = ''
    # text = ''
    # for k in range(len(titles)):
    #     filename = titles[k]+'.txt'
    #     text += wordCloud0(filename)
    # wordCloud1(text)
    # for k in range(len(titles)):
    #     filename = titles[k]+'.txt'
    #     target_id = target_ids[k]
    #     print(filename,target_id)
    #     i = 0
    #     # content = [0]
    #     # while(content): 
    #     #     timestamp =30*i+15
    #     #     i += 1
    #     #     try:
    #     #         content = get_danmu(target_id,timestamp)
    #     #     except:
    #     #         content = []
    #     #     write_file(filename,content)
    #     wordCloud(filename)


if __name__ == "__main__":
    main()
    # content =get_danmu(2235)
    # print(content)
    # cid = 'k0042f69enx'
    # get_targetID(cid)
