# 项目需要配置webdriver到path路径和安装firefox浏览器
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from bs4 import BeautifulSoup
from urllib import request
import getopt
import sys
import tempfile
import os
import uuid


class Bplz:

    def __init__(self):
        pass

    def downloadRun(self, bufferTime, url):
        directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid1()))
        if not os.path.exists(directory):
            os.makedirs(directory)

        print("您可以去" + directory + "下查看具体下载情况")

        # 设置不显示浏览器窗体
        firefox_options = Options()
        firefox_options.add_argument('--headless')

        browser = webdriver.Firefox(options=firefox_options,
                                    executable_path=r"..\Lib\site-packages\bplz\geckodriver.exe")
        browser.get(url)

        time.sleep(bufferTime)
        elem = browser.find_element_by_id("infos")
        html = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        readys = soup.find_all(id='ready')
        filename = 1
        for ready in readys:
            filename += 1
            readyUrl = ready.contents[0].contents[3].attrs['href']
            # print(ready.contents[0].contents[3].attrs['href'])

            req = request.Request(readyUrl)
            req.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36")

            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.dir', directory)
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference("browser.download.manager.showAlertOnComplete", False)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                                   'application/octet-stream')  # 对应header里面的content-type

            browser1 = webdriver.Firefox(firefox_profile=profile, options=firefox_options,
                                         executable_path=r"..\Lib\site-packages\bplz\geckodriver.exe")

            try:
                response = request.urlopen(req, timeout=10)
                singleHtml = response.read().decode("utf-8")
                singleSoup = BeautifulSoup(singleHtml, 'html.parser')
                downloadPageUrl = "https://www.lanzous.com/" + singleSoup.find('iframe').attrs['src']

                browser1.get(downloadPageUrl)
                print("获取下载链接成功：" + downloadPageUrl)
                time.sleep(bufferTime)
                browser1.find_element_by_tag_name('a').click()
                print("开始下载链接：" + downloadPageUrl)

                # browser.get(downloadPageUrl)
                # downloadElem = browser.find_element_by_id('go')
                # time.sleep(1)
                # downloadFileUrl = BeautifulSoup(downloadElem.get_attribute('innerHTML'), 'html.parser').contents[0].attrs['href']
                #
                # print(downloadFileUrl)

            except:
                print("文件获取失败")
                sys.exit()

            finally:
                browser1.close()

        while len([lists for lists in os.listdir(directory) if os.path.isfile(os.path.join(directory, lists))]) < len(
                readys):
            time.sleep(2)

        print("下载完成，正进行后续处理。。。。")
        time.sleep(4)
        browser.close()
        browser.quit()
        browser1.quit()

        return directory

    def getRealZip(self, directory):
        filelist = os.listdir(directory)
        count = []
        for i in range(len(filelist)):
            count.append(len(filelist[i]))
        minIndex = count.index(min(count))
        file_name = os.path.join(directory, filelist[minIndex])
        return file_name

    def rename(self, directory, file_name):
        filelist = os.listdir(directory)

        for i in range(len(filelist)):
            # 设置旧文件名（就是路径+文件名）
            oldname = os.path.join(directory, filelist[i])  # os.sep添加系统分隔符
            # 设置新文件名
            if oldname != file_name:
                newname = os.path.join(directory, filelist[i].replace("%25", ".").replace("%", ".").replace(".zip", ""))
            else:
                newname = os.path.join(directory, filelist[i].replace("%25", ".").replace("%", "."))
            os.rename(oldname, newname)  # 用os模块中的rename方法对文件改名
            print(oldname, '======>', newname)

    def main(self, argv):
        buftime = 2
        url = 'https://www.lanzous.com/b00t9lyqf'

        try:
            opts, args = getopt.getopt(argv, "hb:u:f:", ["buftime=", "url="])
        except getopt.GetoptError:
            print('python bplz.py - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                  '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                print('python bplz.py - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                      '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n')
                sys.exit()
            elif opt in ("-b", "--buftime"):
                buftime = arg
            elif opt in ("-u", "--url"):
                url = arg

        if len(opts) == 0:
            print('python bplz.py - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                  '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n')
            sys.exit()
        print('网页加载缓冲时间：', buftime)
        print('蓝奏云文件夹共享网址：', url)

        directory = self.downloadRun(int(buftime), url)
        file_name = self.getRealZip(directory)
        print("开始修改文件名")
        self.rename(directory, file_name)
        print("文件下载完毕，放置位置为：" + directory)
