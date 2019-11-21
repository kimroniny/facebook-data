#-*- coding:utf-8 -*-
import re, json

def load_cookie():
    with open('cookie', 'r') as f:
        data = json.load(f)
        f.close()
        return data

url = 'https://m.facebook.com/'
url_user_pattern = 'https://m.facebook.com/{name}?v=timeline'

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


# headers have to come from firefox browser, because only in firefox can url pattern work
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
           'Connection':'close'}