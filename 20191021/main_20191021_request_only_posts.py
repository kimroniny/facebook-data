# -*- coding: utf-8 -*-

# 根据现有的posts_url
# 仅仅抓取comments

import re, requests, xlwt, json, time, traceback, xlrd
from xlutils.copy import copy
from collections import defaultdict
from configuration.configuration import *
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote  # url编码解码
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

import os

program_dir = os.path.abspath(os.path.dirname(__file__))

links_id = 2

urls = ['https://m.facebook.com/Vote4LGBT/', 'https://m.facebook.com/Hope.family.tw/']

account_url = urls[links_id - 1]

session = requests.session()
session.mount(host, DESAdapter())
cnt_close = 0

post_all_nums = 0  # 所有的post数量
comment_all_nums = 0  # 所有的评论数量


def workData(posts):
    global session, post_all_nums, comment_all_nums
    all_posts = []  # 所有的post内容
    all_comments = defaultdict(list)  # 所有的评论
    for cnt, link in enumerate(posts):
        comment_r = session.get(
            url=link,
            **params
        )
        print("comment_url_{}: {}".format(post_all_nums, comment_r.url))
        # 有的链接失效了，可能会发生重定向操作，所以要进行状态码检测
        if comment_r.status_code != 200:
            print("Continue Operator: {}, {}".format('comment_r.status_code != 200', comment_r.status_code))
            continue
        soup_post = BeautifulSoup(comment_r.text, 'lxml')
        # analysis post content
        if comment_r.url.startswith(account_url + 'photos'):
            p = soup_post.find('div', attrs={'class': 'msg'})
            p_content = "" if not p else p.text
        elif comment_r.url.startswith('https://m.facebook.com/events'):
            p = soup_post.find_all('h3')
            p = p[1] if p else None
            p_content = "" if not p else p.text
        elif comment_r.url.startswith('https://m.facebook.com/notes'):
            print("Info: notes continue")
            continue
        else:
            p = soup_post.find('div', attrs={'id': 'm_story_permalink_view'})
            p_content = ""
            if p and len(p.contents):
                if len(p.contents[0].contents):
                    if len(p.contents[0].contents[0].contents):
                        p_content = p.contents[0].contents[0].contents[0].contents[1].text
        p = soup_post.find('abbr')
        p_time = "" if not p else p.text
        all_posts.append((post_all_nums, p_time, p_content, comment_r.url))
        post_all_nums += 1
        print("post_time: {}".format(p_time))
        print("post_content: {}".format(p_content))
    return all_posts


wb_post = xlwt.Workbook()
sheet_post = wb_post.add_sheet('post')
count_post = 0
wb_comment = xlwt.Workbook()
sheet_comment = wb_comment.add_sheet('post')
count_comment = 0


def write_excel(posts, posts_xls):
    global count_comment, count_post
    for idx, post in enumerate(posts):
        sheet_post.write(count_post, 0, post[0])
        sheet_post.write(count_post, 1, post[1])
        sheet_post.write(count_post, 2, post[2])
        sheet_post.write(count_post, 3, post[3])
        count_post += 1
    wb_post.save(posts_xls)


links_dir = os.path.join(
    program_dir,
    'links'
)
links_path = os.path.join(
    links_dir,
    'links_{}.txt'.format(links_id)
)
result_dir = os.path.join(
    program_dir,
    'result',
)
posts_excel_file = os.path.join(
    result_dir,
    str(links_id),
    'new_posts2.xls'
)

with open(links_path, 'r') as f:
    alls = f.readlines()

step = 1
point = 0

while point < len(alls):
    links = alls[point:point + step]
    try:
        all_posts = workData(links)
        write_excel(
            all_posts,
            posts_excel_file,
        )
        point += step
    except Exception as e:
        traceback.print_exc()
        session.close()
        print("session closed")
        print("restart scratch.....")
        time.sleep(10)
        session = requests.session()
        session.mount(host, DESAdapter())
        print("session connection build !")
        print("restart successfully !")
