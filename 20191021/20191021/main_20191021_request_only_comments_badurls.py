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

def load_record():
    with open('restore.json', 'r') as f:
        return json.load(f)

def writeBadCommentUrls(url):
    with open('bad_comment_urls.txt', 'w') as f:
        f.write(url + "\n")

def writeBadPostUrls(url):
    with open('bad_post_urls.txt', 'w') as f:
        f.write(url + "\n")

def tryint(s: str):
    res = -1
    try:
        res = int(s)
    except Exception:
        res = -1
    return res

cookies = load_cookie()
host = 'https://m.facebook.com'
params = {"cookies": cookies,
          "headers": headers,
          "allow_redirects": False}

post_all_nums = 0                   # 所有的post数量
comment_all_nums = 0                # 所有的评论数量
all_posts = []                      # 所有的post内容
all_comments = defaultdict(list)    # 所有的评论

url0 = 'https://m.facebook.com/Vote4LGBT/'
url1 = 'https://m.facebook.com/Hope.family.tw/'

with open('links/good_links.txt', 'r') as f:
    goods = f.readlines()

with open('links/bad_links.txt', 'r') as f:
    bads = f.readlines()

session = requests.session()
session.mount(host, DESAdapter())

try:
    for link in bads:
        time.sleep(1)
        session = requests.session()
        session.mount(host, DESAdapter())
        comment_r = session.get(
            url=link,
            **params
        )
        print("comment_url: {}".format(comment_r.url))
        # 有的链接失效了，可能会发生重定向操作，所以要进行状态码检测
        if comment_r.status_code != 200:
            print("Continue Operator: {}, {}".format('comment_r.status_code != 200', comment_r.status_code))
            continue

        soup_post = BeautifulSoup(comment_r.text, 'lxml')

        with open('html.html', 'wb') as f:
            f.write(comment_r.text.encode())
            print('write finish')
        # analysis post content
        if comment_r.url.startswith('https://m.facebook.com/Vote4LGBT/photos'):
            p = soup_post.find('div', attrs={'class': 'msg'})
        else:
            p = soup_post.find_all('h3')
            p = p[1] if p else None
        p_content = "" if not p else p.text
        # analysis post time
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

            comments = soup.find_all('div', attrs={'id': re.compile('^[0-9]{15}$')})

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

            more_comments = soup.find('div', attrs={'id': re.compile('^see_next_[0-9]{15}$')})

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
        session.close()

except Exception as e:
    print(traceback.print_exc())

finally:
    session.close()

    wb = xlwt.Workbook()
    sheet_post = wb.add_sheet('post')
    count = 0
    for idx, post in enumerate(all_posts):
        sheet_post.write(count, 0, idx + 1)
        sheet_post.write(count, 1, post[0])
        sheet_post.write(count, 2, post[1])
        sheet_post.write(count, 3, post[2])
        count = count + 1
    wb.save("result/posts_bad.xls")

    wb = xlwt.Workbook()
    sheet_comment = wb.add_sheet('post')
    count = 0
    for key, value in all_comments.items():
        for (idx, val) in value:
            sheet_comment.write(count, 0, key)
            sheet_comment.write(count, 1, idx)
            sheet_comment.write(count, 2, val)
            count = count + 1
    wb.save("result/comments_bad.xls")


