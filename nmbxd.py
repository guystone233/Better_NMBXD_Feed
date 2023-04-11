import requests
import json
import webbrowser
import time
import threading
import os
from jinja2 import Template
DEFAULT_FORUM = '综合版1'
DEFAULT_PAGES = 20
URL_FORUM_LIST = 'https://api.nmb.best/api/getForumList'
URL_SHOWF = 'https://api.nmb.best/api/showf'
URL_POST_PREFIX = 'https://www.nmbxd1.com/t/'
URL_IMG_PREFIX = 'https://image.nmb.best/image/'
userMode = True
#userhash: 从浏览器中获取
userhash = ''
# 读入模板
currentFileDir = os.path.dirname(__file__)
htmlTemplate = open(currentFileDir + '/template.html',
                    'r', encoding='utf-8').read()
htmlArticles = []


def getForumList():
    # 获取论坛列表,返回dict
    r = requests.get(URL_FORUM_LIST)
    return json.loads(r.text)


def getForumContent(id, page=1):
    # 获取论坛内容,返回dict
    r = requests.get(URL_SHOWF, params={'id': id, 'page': page},cookies={'userhash':userhash})
    return json.loads(r.text)


def fetchContent(forum_id, results, page):
    try:
        content = getForumContent(forum_id, page)
        # print(content)
        results[page] = content
    except Exception as e:
        print(f"Error fetching content for forum id {forum_id}: {e}")


forumList = getForumList()
threads = []
results = {}
for i, forums in enumerate(forumList):
    print(forums['name']+': ' + str(i))
print('其他: 获取{0}的{1}页内容'.format(DEFAULT_FORUM, DEFAULT_PAGES))
# 用户输入板块组编号
try:
    forumsNum = int(input('请输入板块组编号: '))
    forums = forumList[forumsNum]
except:
    userMode = False
if userMode:
    for i, forum in enumerate(forums['forums']):
        print(forum['name']+': '+str(i))
    # 用户输入板块编号
    while True:
        try:
            forumNum = int(input('请输入板块编号: '))
            forumToFetch = forums['forums'][forumNum]
            break
        except:
            print('错误的板块编号')
    while True:
        try:
            pageCount = int(input('请输入要获取的页数: '))
            break
        except:
            print('请输入数字')
else:
    for forums in forumList:
        for forum in forums['forums']:
            if(forum['name'] == DEFAULT_FORUM):
                forumToFetch = forum
    pageCount = DEFAULT_PAGES
    if forumToFetch == None:
        print('未找到{0}'.format(DEFAULT_FORUM))
        exit()
# 获取板块内容
start = time.time()
for page in range(1, pageCount+1):
    thread = threading.Thread(
        target=fetchContent, args=(forumToFetch['id'], results, page))
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
for page in range(1, pageCount+1):
    for post in results[page]:
        img = ""
        try:
            if (post['img'] != ""):
                img = URL_IMG_PREFIX+post['img']+post['ext']
        except:
            print("获取第{0}页失败,可能由于部分板块需要使用饼干才能访问,需要配置userhash".format(page))
            continue
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
