# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
from pyquery import PyQuery as pq



browser = webdriver.Chrome()
# SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)  # 无界面运行
wait = WebDriverWait(browser, 10)

browser.set_window_size(1400, 900)

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

def search():
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        submit.click()
        totle = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))

        get_products()

        return totle.text
    except TimeoutError:
        return search()  # 重新请求


def next_page(page_number):
    print('正在翻页')
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()  # 执行翻页操作
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))

        get_products()

    except TimeoutError:
        next_page(page_number)


def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text().replace('\n', ''),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text().replace('\n', ''),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()

        }
        print(product)

def main():
    try:
        total = search()  # 共100页，
        total = int(re.compile('(\d+)').search(total).group(1))  # 取数字100
        print(total)  # 100
        for i in range(2,total+1):
            next_page(i)
    except Exception:
        print('出错啦')
    finally:
        browser.close()



















































