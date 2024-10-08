import time
from selenium import webdriver
import re
import json

driver = webdriver.Chrome()

objects = []
def extract_links(text):
  pattern = r'listing_block swiper-slide.*?href="/ru/subject/([^"]*)"'
  matches = re.findall(pattern, text)
  return matches

def get_exib( page):
    url = f"https://ar.culture.ru/ru/tag/klassichekoe-iskusstvo#{page}"
    driver.get(url)
    time.sleep(1)
    page_source = driver.execute_script("return document.documentElement.outerHTML;")
    return extract_links(page_source)

for x in range(1, 114):
    objects += get_exib(x)

with open('../data/objects.json', "w") as f:
    json.dump(dict({"objects": objects}), f)
