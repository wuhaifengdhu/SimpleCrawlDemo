##前言
在科研项目中，数据是不可缺少的一部分。而有时候，大部分数据不能通过直接的手段（如网站提供的Restful API）获得，只能自己从网上采集。这个时候，一个简单的爬虫就能解决问题。当然，爬取数据的时候也需要遵守网站的相关法规，阅读网站的robot.txt的文件。       
古语有云，“谋定而后动”，爬取一个网站的数据也是如此。在动手写code之前，首先要结合想要爬取的数据，分析对应网站的结构，理清爬取数据的流程，和每个环节的页面解析和数据采集工作。     
闲言少叙，下面以python语言为例，讲解一下如何爬取数据。

####一，基本技能：   
（1）下载网页源文件
无认证网页下载，python request实现：  
```
import requests
def get_web_source(web_url):
    response = requests.get(web_url)
    return response.content
```

有认真网页下载，python request实现：   

```
import requests
def get_web_source_with_auth(web_url, user_name, password):
    response = requests.get(web_url, auth=(user_name, password))
    return response.content
```

更多request的介绍,参考：https://pypi.python.org/pypi/requests   

(2) 解析网页源文件   
Example： 获取网页源文件中具有property=“org:description”的meta的内容的函数     

```
from bs4 import BeautifulSoup
def get_post_information(web_source):
    soup = BeautifulSoup(web_source, "lxml")
    meta = soup.find('meta', {"property": "og:description"})
    return meta['content'] if meta is not None else None
```

更多beautifulSoup的介绍，参考：https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/

####二， 进阶技能    

1， 程序下载的网页跟我们审查浏览器的的源代码不一样  

我们通过python爬虫爬到的页面内容并不一定与我们看到的一致，可能某些在网页源码中存在的关键标签在爬下来的页面里面找不到了。比如这位弟兄碰到的情况：http://ask.csdn.net/questions/212036
问题产生的原因，程序获取的页面内容是立刻马上的，而很多网站上的一些内容是异步返回的，所以这个时候，你程序获取的页面并不是完整的页面。对于这种情况，可以用selenium或者phantom模拟浏览器实现。    
第一步，构建web driver （selenium和phantom二者取一即可）     
对于selenium，运行程序之前需要安装selenium和下载driver，[下载链接](http://selenium-python.readthedocs.io/installation.html#drivers)

```
import os
from selenium import webdriver
def get_selenium_driver(chrome_driver_path):
    os.environ["webdriver.chrome.driver"] = chrome_driver_path
    return webdriver.Chrome(chrome_driver_path)
```

更多关于selenium的介绍，参考：http://selenium-python.readthedocs.io/    
对于phamtom，运行程序前需要安装phamtom JS，[下载链接](http://phantomjs.org/download.html)    

```
from selenium import webdriver
def get_phantom_driver():
    phantom_js_path = "/usr/local/lib/node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs”    
    return webdriver.PhantomJS(executable_path=phantom_js_path)
```

更多关于[phamtom的介绍](http://phantomjs.org/)    

第二步，利用构建好的web driver download网页    

```
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
```
通过上面的代码可以实现完整网页的下载。上述代码实现的逻辑是，浏览器会一直等待页面加载，直到出现id等于clientPageInstance的标签（这个标签需要自己去观察页面下载过程找到）出现，这时候表明网站加载完全了，才返回网页源码。    

2， 如何规避服务端的机器人检测     
（1）判定为机器人的rule 1: 通过header反爬虫      
默认情况，你通过python去爬取网页，在header中的User-Agent会有python字样，这样就很容易暴露了你机器人的本质。     
应对策略：利用fake_useragent随机产生User-Agent突破限制     
```
from fake_useragent import UserAgent
def anti_rule1(web_url, user_name, password):
    response = requests.get(web_url, auth=(user_name, password), headers={'User-Agent': UserAgent()})
    return response.content
```
更多关于[fake_useragent的介绍](https://pypi.python.org/pypi/fake-useragent) 

（2）判定为机器人rule 1:  获取页面频率过快    
应对策略：设置随机漫步，模拟人类浏览网页的频率。      
```
def anti_rule2(web_url, user_name, password):
    time.sleep(random.uniform(3.6, 7.8))
    return DemoHelper.get_web_source_with_auth(web_url, user_name, password)
```
（3）判定为机器人rule 2：账号单位时间（1小时）持续访问总数超限    
应对策略：多个账号交替爬取数据  
```
def anti_rule3(url_list, user_list, page_limit):
    page_viewed = 0    used_account = 0    web_source_list = []
    for url in url_list:
        if page_viewed % page_limit == 0:
            user_name, password = user_list[used_account % len(user_list)]
            used_account += 1        page_viewed += 1        web_source_list.append(DemoHelper.get_web_source_with_auth(url, user_name, password)) 
    return web_source_list
```
（4）判定为机器人rule 4: 单个IP持续访问总数超限     
应对策略：尽量隐藏自己的真实IP，利用IP代理突破限制    
以PHP的网站为例，它们主要通过以下三个参数获取客户端的IP地址：   
$_SERVER['REMOTE_ADDR'] :客户端IP，也有可能是代理IP   
$_SERVER['HTTP_CLIENT_IP']:代理端的IP，可能存在，也可能伪造    
$_SERVER['HTTP_X_FORWARD_FOR'] ：用户在哪个ip上使用的id，可能存在，也可能伪造   

```
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
def anti_rule4(web_url, user_name, password):
    req_proxy = RequestProxy()
    response = req_proxy.generate_proxied_request(web_url, auth=(user_name, password))
    return response.content
```
更多关于IP代理[http_request_randomizer的介绍](https://pypi.python.org/pypi/http-request-randomizer)

（5）判定为机器人rule 5：单个设备访问次数超限     
你可能会发现，当你突破了账户，IP限制等上述种种限制，账户还是莫名其妙的被黑，那么很可能还有其他方式，能够确定你是你，比如浏览器中的cookie。网站会在你第一次登录的时候，在你的local存了cookie有DID，VID，下次你访问的时候，虽然IP变了，账号变了，但是设备没变，它还是能够确定你的身份。      
应对策略：定时清理cookie    
```
def anti_rule5(web_driver):
    web_driver.delete_all_cookies()
```

##后记
要想写一个牛逼的爬虫必须对反爬虫的原理和技术足够的了解，要想成为反爬虫的专家，也需要对爬虫的手段有足够的认识。故孙子曰：知彼知己，百战不殆。
附本文所有[代码地址](https://github.com/wuhaifengdhu/SimpleCrawlDemo)

 







