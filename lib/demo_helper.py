#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import random
import time
from fake_useragent import UserAgent
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy


class DemoHelper(object):
    @staticmethod
    def get_web_source(web_url):
        response = requests.get(web_url)
        return response.content

    @staticmethod
    def get_web_source_with_auth(web_url, user_name, password):
        response = requests.get(web_url, auth=(user_name, password))
        return response.content

    @staticmethod
    def get_org_description(web_source):
        soup = BeautifulSoup(web_source, "lxml")
        meta = soup.find('meta', {"property": "og:description"})
        return meta['content'] if meta is not None else None

    @staticmethod
    def get_phantom_driver(phantom_js_path):
        # phantom_js_path = "/usr/local/lib/node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs"
        return webdriver.PhantomJS(executable_path=phantom_js_path)

    @staticmethod
    def get_selenium_driver(chrome_driver_path):
        os.environ["webdriver.chrome.driver"] = chrome_driver_path
        return webdriver.Chrome(chrome_driver_path)

    @staticmethod
    def login(web_driver, login_url, user_name, password):
        web_driver.get(login_url)
        web_driver.find_element_by_id('login_field').send_keys(user_name)
        web_driver.find_element_by_id('password').send_keys(password)
        web_driver.find_element_by_name("commit").click()

    @staticmethod
    def get_web_source(web_driver, url):
        web_driver.get(url)
        delay = 5  # delay seconds
        try:
            WebDriverWait(web_driver, delay).until(
                EC.presence_of_element_located((By.ID, 'clientPageInstance')))
            print("Page is ready!")
            return web_driver.page_source
        except TimeoutException:
            print("Loading took too much time!")
            return None

    @staticmethod
    def anti_rule1(web_url, user_name, password):
        response = requests.get(web_url, auth=(user_name, password), headers={'User-Agent': UserAgent()})
        return response.content

    @staticmethod
    def anti_rule2(web_url, user_name, password):
        time.sleep(random.uniform(3.6, 7.8))
        return DemoHelper.get_web_source_with_auth(web_url, user_name, password)

    @staticmethod
    def anti_rule3(url_list, user_list, page_limit):
        page_viewed = 0
        used_account = 0
        web_source_list = []
        for url in url_list:
            if page_viewed % page_limit == 0:
                user_name, password = user_list[used_account % len(user_list)]
                used_account += 1
            page_viewed += 1
            web_source_list.append(DemoHelper.get_web_source_with_auth(url, user_name, password))
        return web_source_list

    @staticmethod
    def anti_rule4(web_url, user_name, password):
        req_proxy = RequestProxy()
        response = req_proxy.generate_proxied_request(web_url, auth=(user_name, password))
        return response.content

    @staticmethod
    def anti_rule5(web_driver):
        web_driver.delete_all_cookies()
