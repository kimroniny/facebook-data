#-*- coding: utf-8 -*-

# abandon
# 使用selenium

import time, json, sys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from configuration.configuration import email, password, url
# sys.path.append('../')

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
# driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox(executable_path='../geckodriver.exe')

driver.get(url=url)
login_email = driver.find_element_by_id('m_login_email')
login_password = driver.find_element_by_xpath('//input[@type="password"]')
login_submit = driver.find_element_by_xpath('//input[@type="submit" and @name="login"]')

login_email.clear()
login_email.send_keys(email)
login_password.clear()
login_password.send_keys(password)
login_submit.click()

input()

url0 = 'https://m.facebook.com/Vote4LGBT/?epa=SEARCH_BOX'
url1 = 'https://m.facebook.com/Hope.family.tw/'
driver.get(url=url0)

input()

def checkDate(s):
    return False

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    post_divs = driver.find_elements_by_xpath("//div[@class='' and style='padding-top:8px']")
    issue_time = post_divs[-1].find_elements_by_tag_name('a')[2].text
    if not checkDate(issue_time): break
    input()

post_divs = driver.find_elements_by_xpath("//div[@class='' and style='padding-top:8px']")
comment_links = [div.find_elements_by_tag_name('a')[-2].get_attribute('href') for div in post_divs]

























