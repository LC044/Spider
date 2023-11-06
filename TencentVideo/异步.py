# -*- coding : utf-8-*-

import asyncio
import json
import os
import aiofiles
import aiohttp
import jieba
from matplotlib.pyplot import title
import requests
import time
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

'''
创建路径
'''


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if os.path.exists(path):
        return False
    os.makedirs(path)
    return True


def get_cid(videoName):  # ! 获取片名的cid
    url = f'https://v.qq.com/x/search/?q={videoName}&stag=2&smartbox_ab='
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
        'cookie': 'pgv_pvid=6766918384; tvfe_boss_uuid=8aabd9b75a8cf9e4; bucket_id=9231006; ts_uid=6467769376; RK=tM9gYEP0dJ; ptcz=38a3eccf78b58f599f70a36c1661f18acd222285d622c216bb6049616f3413ee; luin=o0863909694; o_cookie=863909694; ptui_loginuin=616347231; video_guid=15fa8088c86ca82a; video_platform=2; vuserid=321471598; lw_nick=%E5%8F%B8%22%E8%BF%9C|863909694|http://thirdqq.qlogo.cn/g?b=oidb&k=Q9JRFq92Kcyt0b9akZEBRQ&s=640&t=1584197254|0; QQLivePCVer=50221213; main_login=qq; lskey=0001000034d04dcc34af470f36cb96ef838f703f52d3f2cf3e38aa1abda73380afeb07af857499f4606b7de2; pgv_info=ssid=s5906794330; ts_refer=www.sogou.com/web; vusession=Yql8FQXF5yYjEPg90ImAyg..; tvfe_search_uid=ecdc882e-262e-47e2-914c-9f50776219e6; txv_boss_uuid=316a22ac-bcbd-c7d7-2bba-2b7b97c42fd4; vversion_name=8.2.95; video_omgid=15fa8088c86ca82a; qv_als=y710jwmpaINfmSVKA11647997243rTpkoA==; uid=393142431; ad_play_index=87; ts_last=v.qq.com/x/search/; ptag=www_sogou_com|x',

    }
    resp = requests.get(url, headers=headers)
    page = BeautifulSoup(resp.text, 'html.parser')
    content = page.find('div', class_="_infos")
    a = content.find('a')
    href = a.get('href')
    cid = href.split('/')[-1].rstrip(".html")
    # print(cid)
    return cid


def getVid(cid):  # !获取所有视频的vid
    headers = {
        "cookie": "pgv_pvid=6766918384; tvfe_boss_uuid=8aabd9b75a8cf9e4; video_platform=2; video_guid=15fa8088c86ca82a; RK=tM9gYEP0dJ; ptcz=38a3eccf78b58f599f70a36c1661f18acd222285d622c216bb6049616f3413ee; luin=o0863909694; lskey=00010000596e1de133d5203ddd766d8050ee4591b6fcfa1ab8d505a90e3bcc3c7d4cbbcef236ee77fac99c50; o_cookie=863909694; ptui_loginuin=616347231; pgv_info=ssid=s3352981908; main_login=qq; vuserid=321471598; vusession=zKyNjJh6LMR8x2DCWBB8bQ..; login_time_init=1647866493; _video_qq_version=1.1; _video_qq_main_login=qq; _video_qq_appid=3000501; _video_qq_vuserid=321471598; _video_qq_vusession=zKyNjJh6LMR8x2DCWBB8bQ..; _video_qq_login_time_init=1647866493; video_omgid=15fa8088c86ca82a; vversion_name=8.2.95; next_refresh_time=6566; _video_qq_next_refresh_time=6566; login_time_last=2022-3-21 20:42:6; uid=393142431",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
        "referer": "https://v.qq.com/",
    }
    payload = {
        "has_cache": 1,
        "page_params": {
            "cid": cid,
            "id_type": "1",
            "lid": "",
            "page_context": "",
            "page_id": "vsite_episode_list",
            "page_num": "",
            "page_size": "60",
            "page_type": "detail_operation",
            "req_from": "web",
            "vid": "b0035jy832t",
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


async def get_targetID(vid, session):  # ! 获取targetID
    url = "https://access.video.qq.com/danmu_manage/regist?vappid=97767206&vsecret=c0bdcbae120669fff425d0ef853674614aa659c605a613a4&raw=1"
    payload = {"wRegistType": 2,
               "vecIdList": [vid],
               "wSpeSource": 0,
               "bIsGetUserCfg": 1,
               "mapExtData": {
                   vid: {
                       "strCid": "mzc00200acwia9w",
                       "strLid": ""
                   }
               }
               }
    async with session.post(url, json=payload) as resp:
        data = await resp.json()
        dat = data['data']['stMap'][vid]['strDanMuKey']

        target_id = dat.split('targetid=')[-1]
        # print(target_id)
    return target_id


async def get_danmu(target_id, timestamp, session):  # ! 获取弹幕
    Payload = {
        "otype": "json",
        "callback": "jQuery19104233449465496275_1647866555917",
        "target_id": target_id,
        # 7712619175&vid=k0042f69enx
        "session_key": "0,745,1647867972",
        "timestamp": timestamp,
        "_": "1647866555922",
    }
    # url = 'https://mfm.video.qq.com/danmu'
    url = f'https://dm.video.qq.com/barrage/segment/{target_id}/t/v1/{timestamp-30000}/{timestamp}'
    print(url)
    async with aiohttp.ClientSession() as session:
        # async with session.get(url, data=Payload) as resp:
        async with session.get(url) as resp:
            data = await  resp.json()
            barrage_list = data['barrage_list']
            content = []
            for comment in barrage_list:
                danmu = comment['content']
                content.append(danmu)
            if (content):
                print(content)
            else:
                print("waiting!!!!")
    return content


async def write_file(filename, content):  # ! 将内容写入文件
    async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
        for c in content:
            await f.writelines(f'{c};')


def trans_CN(text):  # ! 中文分词
    word_list = jieba.cut(text)
    result = " ".join(word_list)
    return result


def wordCloud(file):  # ! 生成词云
    f = open(file, 'r', encoding='utf-8')
    text = f.read()
    f.close
    text = trans_CN(text)
    content = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords = set()
    stopwords.update(content)

    wordcloud = WordCloud(
        # 添加遮罩层
        # mask=mask,
        # 生成中文字的字体,必须要加,不然看不到中文
        width=1600,
        height=1200,
        stopwords=stopwords,
        font_path="C:\Windows\Fonts\STXINGKA.TTF"
    ).generate(text)
    # image_produce = wordcloud.to_image()
    filename = file.rstrip('.txt') + '.png'
    wordcloud.to_file(filename)
    print(f"{filename} has been built successfully !!!")


async def download(filename, target_id):  # todo 下载弹幕文件
    print(filename, target_id)
    i = 1
    tasks = []
    target_id = target_id.split('&')[0]
    while (i < 91):
        timestamp = 30000*i  # 弹幕的时间戳，用于url的请求参数
        i += 1
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(get_danmu(target_id, timestamp, session))
            tasks.append(task)

    await asyncio.wait(tasks)
    content = []
    async with aiofiles.open(filename + '.txt', 'a', encoding='utf-8') as f:
        for task in tasks:
            content = task.result()
            if (content):
                for c in content:
                    await f.writelines(c + ';')


async def main(videoName):  # ? 根据剧名获取弹幕
    start_time = time.time()
    mkdir(f'./{videoName}')
    cid = get_cid(videoName)
    vids, titles = getVid(cid)
    target_ids = []
    tasks = []

    async with aiohttp.ClientSession() as session:
        for vid in vids:
            task = asyncio.create_task(get_targetID(vid, session))
            tasks.append(task)
            task.set_result
            # target_id = task.result
        await asyncio.wait(tasks)
    for task in tasks:
        target_ids.append(task.result())
    print(target_ids, titles)

    tasks = []
    for i in range(len(titles)):
        filename = f'./{videoName}/{titles[i]}'
        target_id = target_ids[i]
        task = asyncio.create_task(download(filename, target_id))
        tasks.append(task)
    await asyncio.wait(tasks)
    print('waiting')
    end_time = time.time()
    print(f'获取弹幕耗时：{int((end_time - start_time) * 100 + 0.5) / 100} seconds')
    print('努力生成弹幕中！！！')

    # 多进程生成词云

    with ProcessPoolExecutor(8) as t:
        for i in range(len(titles)):
            filename = f'./{videoName}/{titles[i]}.txt'
            # wordCloud(filename,content)
            t.submit(wordCloud, filename)
            # print(f'\t{i}')

    end_time = time.time()
    print(f'总耗时：{int((end_time - start_time) * 100 + 0.5) / 100} seconds')


if __name__ == "__main__":
    videoName = input("请输入剧名：\n")  # 开端
    # videoName = '春闺梦里人'
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(videoName))

'''
time = 39.22 minute

timestamp = 2355

num = ( 2355-15 )/30 = 78

(2685-15)/30 = 89
'''
