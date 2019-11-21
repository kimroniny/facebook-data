with open('links.txt', 'r') as f:
    links = f.readlines()

bad_links = []
good_links = []
for link in links:
    if not link.startswith('https://m.facebook.com/story.php'):
        bad_links.append(link)
    else:
        good_links.append(link)

with open('bad_links.txt', 'w') as f:
    f.writelines(bad_links)

with open('good_links.txt', 'w') as f:
    f.writelines(good_links)