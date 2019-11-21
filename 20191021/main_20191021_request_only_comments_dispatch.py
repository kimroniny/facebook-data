#-*- coding: utf-8 -*-

# 根据现有的posts_url
# 仅仅抓取comments

import re,requests,xlwt,json, time, traceback, xlrd
from xlutils.copy import copy
from collections import defaultdict
from configuration.configuration import *
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote # url编码解码
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)

def checkDate(s: str):
    if s.find('2018') > -1: return 0
    if s.find('2017') > -1: return -1
    return 1

def url_decode(s: str):
    return unquote(s).replace('amp;', '')

cookies = load_cookie()
host = 'https://m.facebook.com'
params = {"cookies": cookies,
          "headers": headers,
          "allow_redirects": False}


url0 = 'https://m.facebook.com/Vote4LGBT/'
url1 = 'https://m.facebook.com/Hope.family.tw/'

with open('links/links.txt', 'r') as f:
    alls = f.readlines()

with open('links/good_links.txt', 'r') as f:
    goods = f.readlines()

with open('links/bad_links.txt', 'r') as f:
    bads = f.readlines()

with open('links/rest_links.txt', 'r') as f:
    rests = f.readlines()

session = requests.session()
session.mount(host, DESAdapter())
cnt_close = 0

post_all_nums = 0                   # 所有的post数量
comment_all_nums = 0                # 所有的评论数量


def workData(posts):
    global session, post_all_nums, comment_all_nums
    all_posts = []  # 所有的post内容
    all_comments = defaultdict(list)  # 所有的评论
    for cnt, link in enumerate(alls):
        comment_r = session.get(
            url=link,
            **params
        )
        print("comment_url_{}: {}".format(cnt, comment_r.url))
        # 有的链接失效了，可能会发生重定向操作，所以要进行状态码检测
        if comment_r.status_code != 200:
            print("Continue Operator: {}, {}".format('comment_r.status_code != 200', comment_r.status_code))
            continue

        soup_post = BeautifulSoup(comment_r.text, 'lxml')

        # analysis post content
        if comment_r.url.startwith('https://m.facebook.com/Vote4LGBT/photos'):
            p = soup_post.find('div', attrs={'class': 'msg'})
            p_content = "" if not p else p.text
        elif comment_r.url.startswith('https://m.facebook.com/events'):
            p = soup_post.find_all('h3')
            p = p[1] if p else None
            p_content = "" if not p else p.text
        else:
            p = soup_post.find('div', attrs={'id': 'm_story_permalink_view'})
            p_content = ""
            if p and len(p.contents):
                if len(p.contents[0].contents):
                    if len(p.contents[0].contents[0].contents):
                        p_content = p.contents[0].contents[0].contents[0].contents[1].text

        p = soup_post.find('abbr')
        p_time = "" if not p else p.text
        all_posts.append((p_time, p_content, comment_r.url))
        post_all_nums += 1
        print("post_time: {}".format(p_time))
        print("post_content: {}".format(p_content))

        # 当前post的评论数
        comment_nums = 0
        while True:
            time.sleep(1)
            # set encoding
            comment_r.encoding = 'utf-8'

            soup = BeautifulSoup(comment_r.text, 'lxml')

            comments = soup.find_all('div', attrs={'id': re.compile('^[0-9]{13,17}$')})

            print("评论数量: " + str(len(comments)))

            for idx, comment in enumerate(comments):
                p = comment.contents[0]
                content = p.contents[1].text
                comment_nums += 1
                comment_all_nums += 1
                print('----------[{}], {}----------'.format(comment_nums, comment_all_nums))
                all_comments[post_all_nums].append((comment_nums, content))
                print(str(idx) + '. ' + content)
                print('-' * 20)

            more_comments = soup.find('div', attrs={'id': re.compile('^see_next_[0-9]{13,17}$')})

            if more_comments:
                a = more_comments.find('a')
                if a:
                    more_link = a.attrs['href']

                    time.sleep(1)
                    comment_r = session.get(
                        url=url_decode(host + more_link),
                        **params
                    )
                else:
                    break
            else:
                print("<<<<已经到达当前post的最后评论>>>>")
                break
    return all_posts, all_comments





wb_post = xlwt.Workbook()
sheet_post = wb_post.add_sheet('post')
count_post = 0
wb_comment = xlwt.Workbook()
sheet_comment = wb_comment.add_sheet('post')
count_comment = 0

def write_excel(posts, comments):
    global count_comment, count_post
    for idx, post in enumerate(posts):
        sheet_post.write(count_post, 0, idx + 1)
        sheet_post.write(count_post, 1, post[0])
        sheet_post.write(count_post, 2, post[1])
        sheet_post.write(count_post, 3, post[2])
        count_post += 1
    wb_post.save("result/posts.xls")

    for key, value in comments.items():
        for (idx, val) in value:
            sheet_comment.write(count_comment, 0, key)
            sheet_comment.write(count_comment, 1, idx)
            sheet_comment.write(count_comment, 2, val)
            count_comment += 1
    wb_comment.save("result/comments.xls")

step = 3
point = 0

while point < len(alls):
    links = alls[point:point+step]
    try:
        all_posts, all_comments = workData(links)
        write_excel(all_posts, all_comments)
        point += step
    except Exception as e:
        print("error: " + str(e))
        session.close()
        print("session closed")
        print("restart scratch.....")
        time.sleep(10)
        session = requests.session()
        session.mount(host, DESAdapter())
        print("session connection build !")
        print("restart successfully !")