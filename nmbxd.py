import requests
import json
import webbrowser
import time
import threading
import os
from jinja2 import Template
# 程序执行时间计时（毫秒）
start = time.time()
PAGES = 20
URL_FORUM_LIST = 'https://api.nmb.best/api/getForumList'
URL_SHOWF = 'https://api.nmb.best/api/showf'
URL_POST_PREFIX = 'https://www.nmbxd1.com/t/'
URL_IMG_PREFIX = 'https://image.nmb.best/image/'
# 读入模板
currentFileDir = os.path.dirname(__file__) 
htmlTemplate = open(currentFileDir + '/template.html', 'r', encoding='utf-8').read()
htmlArticles = []


def getForumList():
    # 获取论坛列表,返回dict
    r = requests.get(URL_FORUM_LIST)
    return json.loads(r.text)


def getForumContent(id, page=1):
    # 获取论坛内容,返回dict
    r = requests.get(URL_SHOWF, params={'id': id, 'page': page})
    return json.loads(r.text)


def fetchContent(forum_id, results, page):
    try:
        content = getForumContent(forum_id, page)
        #print(content)
        results[page] = content
    except Exception as e:
        print(f"Error fetching content for forum id {forum_id}: {e}")


forumList = getForumList()
threads = []
results = {}
for forums in forumList:
    for forum in forums['forums']:
        if(forum['name'] == '综合版1'):
            for page in range(1, PAGES+1):
                thread = threading.Thread(
                    target=fetchContent, args=(forum['id'], results, page))
                threads.append(thread)
                thread.start()
for thread in threads:
    thread.join()
for page in range(1, PAGES+1):
    for post in results[page]:
        img = ""
        if (post['img'] != ""):
            img = URL_IMG_PREFIX+post['img']+post['ext']
        htmlArticles.append(
            {'id': post['id'], 'title': post['title'], 'content': post['content'], 'time': post['now'], 'imgUrl': img})
# 渲染模板
html = Template(htmlTemplate).render(
    articles=htmlArticles, post_prefix=URL_POST_PREFIX)
end = time.time()
print(f"Total time: {end - start}")
# 保存为html文件并打开
with open(currentFileDir + '/result.html', 'w', encoding='utf-8') as f:
    f.write(html)
webbrowser.open(currentFileDir + '/result.html')