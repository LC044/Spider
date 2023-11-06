# 一、前言

大家都看视频的时候会发现有好多人在弹幕区讨论视频内容，你有没有好奇过大家都在弹幕里说些什么，接下来这一篇文章就教你如何获取腾讯视频弹幕并将弹幕做成词云图。

运行结果《春闺梦里人》：

![春闺梦里人_01](./assets/春闺梦里人_01.png)

![image-20230326200219616](./assets/image-20230326200219616.png)

# 二、定位数据

第一步肯定是F12抓取网站数据，先看看有没有可以利用的数据

![image-20230326200539829](./assets/image-20230326200539829.png)

找啊找，终于发现一点端倪，这个东西好像有点意思，点开看看

![image-20230326200739654](./assets/image-20230326200739654.png)

这不就是我们想要的数据吗，so easy啊

![image-20230326200836332](./assets/image-20230326200836332.png)

找到URL，试试看能不能get到json数据

![image-20230326200920590](./assets/image-20230326200920590.png)

```Python
import requests
url = 'https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/90000/120000'
resp = requests.get(url)
print(resp.json())
```

![image-20230326201044948](./assets/image-20230326201044948.png)

这也太简单了吧，连防爬措施都没有

先解析一下

```Python
def get_danmu(url):
    resp = requests.get(url)
    barrage_list = resp.json()['barrage_list']
    content = []
    for danmu in barrage_list:
        print(danmu['content'])
        content.append(danmu['content'])
```

![image-20230326201151814](./assets/image-20230326201151814.png)

这就搞定了？再看看

![image-20230326201252992](./assets/image-20230326201252992.png)

再往下翻还有很多弹幕，提取这些URL对比一下

https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/0/30000

https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/30000/60000

https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/60000/90000

https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/90000/120000

https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/120000/150000

规律这不就来了吗，后面两个/数字是30000的倍数

那最后一个是多少呢，不知道，30000*15?

https://dm.video.qq.com/barrage/segment/n0045knbi5b/t/v1/420000/450000

管他呢，多请求几次，等到请求结果为空就停止

```Python
i = 1
while True:
    num = 30000 * i
    url = f'https://dm.video.qq.com/barrage/segment/n0045clizl7/t/v1/{num - 30000}/{num}'
    content = get_danmu(url)
    if not content:
        break
    i += 1
```

这集电视剧弹幕就搞定了

# 三、获取targetID

URL后面的数字解决了，那前面的一串n0045clizl7字符是什么东西

观察一下就会发现，这俩不是一个东西吗

![image-20230326202136243](./assets/image-20230326202136243.png)

那这个targetID从哪来呢？

这时候就要返回一级从外面看了

搜一下

![image-20230326202626166](./assets/image-20230326202626166.png)

查看网页源代码，这不就找到了吗

![image-20230326202706340](./assets/image-20230326202706340.png)

接下来就不用我多说了吧

# 四、性能优化

视频弹幕分为很多集，每集的弹幕有很多片段，每请求一次都要消耗很多网络IO时间，所以按顺序一个个爬取每一集的弹幕会很慢。使用多线程或多进程会提高爬取速度。
但是像这种IO较为频繁的系统，用异步协程能大大节省资源并提升性能。协程能够在IO等待时间就去切换执行其他任务，当IO操作结束后再自动回调。

**协程**（单线程），英文叫coroutine，又称微线程、纤程，是一种运行在用户状态的轻量级线程。它拥有自己的寄存器上下文和栈，在调度切换时，将寄存器上下文和栈保存到其他地方，等切回来时，再恢复到先前保存的寄存器上下文和栈。因此，协程能保留上一次调用时的状态，所有局部状态的一个特定组合，每次过程重入，就相当于进入上一次调用的状态。

1. event_loop：事件循环，相当于一个无限循环，我们可以把一个函数注册到这个事件循环上，当满足发生条件的时候，就调用对应的处理方法。

2. coroutine：协程，指代协程对象类型，我们可以将协程对象注册到事件循环中，它会被事件循环调用。我们可以使用async关键字来定义一个方法，这个方法再调用时不会被立即执行，而是返回一个协程对象

3. task：任务，这是协程对象的进一步封装，包含协程的各个状态

4. future：代表将来执行或者没有执行的任务的结果，实际上和task没有本质区别



* 用协程读写文件

```python
async def write_file(filename, content):  # ! 将内容写入文件  
    async with aiofiles.open(filename, 'a', encoding='utf-8') as f:  
        for c in content:  
            await f.writelines(f'{c};')
```

* 用协程进行网络请求

```python
    async with aiohttp.ClientSession() as session:
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
```

# 五、运行说明

1. 环境配置
   
   ```shell
   pip install -r requirements.txt
   ```

2. 启动文件
   
   ```shell
   python 异步.py
   ```
