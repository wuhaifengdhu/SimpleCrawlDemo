#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.demo_helper import DemoHelper
import os


class Main(object):
    @staticmethod
    def run_script(user_name, password, url="https://github.com/login"):
        driver_file = "chromedriver.exe" if os.name == 'nt' else "chromedriver"
        chrome_driver_path = os.path.join(os.getcwd(), "lib", driver_file)
        driver = DemoHelper.get_selenium_driver(chrome_driver_path)
        DemoHelper.login(driver, url, user_name, password)
        driver.get("https://github.com/wuhaifengdhu/SimpleCrawlDemo")


if __name__ == '__main__':
    # github_user_name = "your-github-user-name"
    github_user_name = "wuhaifengdhu@163.com"
    # github_password = "your-github-password"
    github_password = "wuhaifeng2012"
    Main.run_script(github_user_name, github_password)
