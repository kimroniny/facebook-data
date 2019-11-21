#-*- coding:utf-8 -*-
import re, json

def load_cookie():
    with open('cookie', 'r') as f:
        data = json.load(f)
        f.close()
        return data

def load_crawl_info():
    with open('crawl_info.txt', 'r') as f:
        data = json.load(f)
        f.close()
        return data

url = 'https://m.facebook.com/'
url_user_pattern = 'https://m.facebook.com/{name}?v=timeline'
data = load_crawl_info()
crawl_user_url = data['crawl_user_url']
email = data['email']
password = data['password']
userids_limit = data['userids_limit']

# some url regex patterns about necessary urls
re_more             = '<a href="([^"<>]+)"><span>See More Stories</span></a>'
pattern_more        = re.compile(re_more)

re_article          = 'shared_from_post_id=([0-9]{0,17})'
pattern_article     = re.compile(re_article)

re_userid           = '/a/mobile/friends/add_friend.php\?id=([0-9]{0,20})'
pattern_userid      = re.compile(re_userid)

re_userid_more      = '<a href="(/ufi/reaction/profile/browser/fetch/[^"<>]+)"><span>See More</span></a>'
pattern_userid_more = re.compile(re_userid_more)

re_commentlink      = '<a(?:.[^>]*?)href="(.[^"]*?)"(?:[^>]*?)>(?:[0-9]* Comments|1 Comment|Comment)</a>'
pattern_commentlink = re.compile(re_commentlink)

re_date             = '<abbr>((?:January|February|March|April|May|June|July|August|September|October|November|December)\s[0-9]{1,2}[,\s0-9]*)\sat\s[0-9]{1,2}:[0-9]{1,2}\s(?:PM|AM)</abbr>'
pattern_date        = re.compile(re_date)

re_more_posts       = '<a(?:.[^>]*?)href="(.[^"]*?)"(?:[^>]*?)>Show more</a>'
pattern_more_posts  = re.compile(re_more_posts)

# when your pc starts shadowsocks client, this proxy works
proxies = {
    'http': 'http://127.0.0.1:1080',
    'https': 'https://127.0.0.1:1080'
}

# this proxy now does't work for some unknown reasons
proxies2 = {
    'http': 'http://pxuser:kimroniny@202.165.123.67:3128',
    'https': 'https://pxuser:kimroniny@202.165.123.67:3128'
}

# headers have to come from firefox browser, because only in firefox can url pattern work
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
           'Connection':'close'}
headers_chrome = {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
headers_firefox = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'}

# some configs about excel
sheetname_reaction_ids = 'reaction_ids'