#-*- coding: utf-8 -*-

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

restore_keys = ['post_url', 'post_idx', 'all_posts_nums', 'comment_url', 'comment_idx', 'all_comment_nums']

inherit = False
record = load_record()

# 满足所有的键值
for key in restore_keys:
    if key not in record.keys():
        record[key] = ''

# 关闭备份
if not inherit:
    for key in record.keys():
        record[key] = ''

current_post_url = record['post_url']
current_post_idx = tryint(record['post_idx'])
current_post_nums = tryint(record['all_posts_nums'])
current_comment_url = record['comment_url']
current_comment_idx = tryint(record['comment_idx'])
current_comment_nums = tryint(record['all_comment_nums'])

if current_post_nums == -1: current_post_nums = 0
if current_comment_nums == -1: current_comment_nums = 0

update_comment_url = False

cookies = load_cookie()
host = 'https://m.facebook.com'
params = {"cookies": cookies,
          "headers": headers,
          "allow_redirects": False}

post_all_nums = 0                       # 所有的post数量
comment_all_nums = 0                # 所有的评论数量
all_posts = []                      # 所有的post内容
all_comments = defaultdict(list)    # 所有的评论

url0 = 'https://m.facebook.com/Vote4LGBT/'
url1 = 'https://m.facebook.com/Hope.family.tw/'
# url0 = 'https://m.facebook.com//Vote4LGBT?sectionLoadingID=m_timeline_loading_div_1572591599_0_36_timeline_unit:1:00000000001540388224:04611686018427387904:09223372036854775746:04611686018427387904&unit_cursor=timeline_unit:1:00000000001540388224:04611686018427387904:09223372036854775746:04611686018427387904&timeend=1572591599&timestart=0&tm=AQDXYVJ5_oZEhb6A&refid=17'

if current_post_url == '': current_post_url = url0

session = requests.session()
session.mount(host, DESAdapter())
r = session.get(url=current_post_url, **params)
print('^'*40+'主页'+'^'*40)
print(r.url)
all_post_urls = []
all_comment_urls = []
page_nums = 0
try:
    while True:
        time.sleep(1)

        print('%' * 20 + '正在抓取posts页_{}'.format(page_nums+1) + '%' * 20)
        page_nums += 1
        print(r.url)

        current_post_url = r.url
        all_post_urls.append(current_post_url)

        # 设置编码格式
        r.encoding = 'utf-8'
        html = r.text

        soup0 = BeautifulSoup(html, 'lxml')

        # 获取所有的post块
        post_divs = soup0.find_all('div', attrs={'role': 'article', 'data-ft': re.compile('top_level_post_id')})

        for post_idx, post_div in enumerate(post_divs):
            if post_idx <= current_post_idx:
                print("Continue Operator: {}".format('post_idx <= current_post_idx'))
                continue

            # 判断日期
            datetimes = pattern_date.findall(str(post_div))
            if not datetimes:
                print("Continue Operator: {}".format('not datetimes'))
                continue
            if checkDate(datetimes[0]) == 1:
                print("Continue Operator: {}, {}".format('checkDate(datetimes[0]) == 1', datetimes[0]))
                continue
            if checkDate(datetimes[0]) == -1:
                print("***********日期不符合: " + str(datetimes[0]))
                raise Exception("！！！！！超过时间期限："+str(datetimes[0]))

            # 获取评论链接
            links = pattern_commentlink.findall(str(post_div))
            if not links: continue
            link = links[0]

            time.sleep(1)

            # 是否应该抓取博文内容
            posted = True

            # 抓取评论页面
            if update_comment_url or current_comment_url == '':
                current_comment_url = url_decode(host+link)
                update_comment_url = True

            print("comment_url_{}: ".format(post_idx)+current_comment_url)
            all_comment_urls.append(
                (len(all_post_urls), current_comment_url)
            )

        current_post_idx = -1
        mores = pattern_more_posts.findall(html)
        if len(mores) > 0:
            link_more = url_decode(url + mores[0])
            print("link_more: " + link_more)
            r = session.get(url=link_more, **params)
        else:
            print('*****没有posts了*****')
            raise Exception("！！！！！没有posts了，程序结束")

        current_post_idx = -1

except Exception as e:

    print(traceback.print_exc())
    session.close()

finally:

    wb_post = xlrd.open_workbook('post_urls.xls')
    nrows_post = wb_post.sheet_by_index(0).nrows
    xls_post = copy(wb_post)
    sheet_post = xls_post.get_sheet(0)
    count = nrows_post
    for idx, post in enumerate(all_post_urls):
        sheet_post.write(count, 0, idx + 1)
        sheet_post.write(count, 1, post)
        count = count + 1
    xls_post.save("post_urls.xls")

    wb_comment = xlrd.open_workbook('comment_urls.xls')
    nrows_comment = wb_comment.sheet_by_index(0).nrows
    xls_comment = copy(wb_comment)
    sheet_comment = xls_comment.get_sheet(0)
    count = nrows_comment
    for (key, value) in all_comment_urls:
        sheet_comment.write(count, 0, key)
        sheet_comment.write(count, 1, value)
        count = count + 1
    xls_comment.save("comment_urls.xls")



