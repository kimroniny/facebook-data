from bs4 import BeautifulSoup
import re

re_commentlink      = '<a(?:.[^>]*?)href="(.[^"]*?)"(?:[^>]*?)>(?:[0-9]* Comments|1 Comment|Comment)</a>'
pattern_commentlink = re.compile(re_commentlink)

with open('posts.html', 'rb') as f:
    a = f.read()
soup = BeautifulSoup(a.decode('utf-8'), 'lxml')
divs = soup.find_all('div', attrs={'data-sigil': "reactions-bling-bar"})
articles = soup.find_all('article')
for idx, item in enumerate(articles):
    footer = item.find('footer')
    if footer:
        cnt_link = str(pattern_commentlink.findall(str(item))[0])
        content = footer.find('div', attrs={'data-sigil':"reactions-bling-bar"})
        print("-"*30)
        print(cnt_link)
        num_reaction = num_share = num_comment = 0
        if content:
            reaction = content.find('div', attrs={"data-sigil":"reactions-sentence-container"})
            if reaction:
                num_reaction = str(reaction.text)
                num_reaction = re.sub('\s+', ' ', num_reaction)
            comment = re.findall(r'([0-9]+)\s[Comment|Comments]', str(content))
            if comment:
                num_comment = comment[0]
            share = re.findall(r'([0-9]+)\s[Share|Shares]', str(content))
            if share:
                num_share = share[0]
        link = 'https://m.facebook.com' + cnt_link[:cnt_link.find('?')+1]

