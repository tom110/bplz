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
import bplz
from subprocess import Popen, PIPE, STDOUT
import zipfile
from selenium.common.exceptions import WebDriverException
import psutil
from urllib.parse import quote, unquote


class Bplz:

    def __init__(self):
        pass

    def isExist(self, dir, etentName):
        Files = os.listdir(dir)
        for k in range(len(Files)):
            # 提取文件夹内所有文件的后缀
            Files[k] = os.path.splitext(Files[k])[1]

        # 你想要找的文件的后缀
        if etentName in Files:
            return True
        else:
            return False

    def downloadRun(self, bufferTime, url):
        p = Popen("taskkill /IM firefox.exe /F", stdout=PIPE, stderr=STDOUT)
        directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid1()))
        if not os.path.exists(directory):
            os.makedirs(directory)

        print("您可以去" + directory + "下查看具体下载情况")

        # 设置不显示浏览器窗体
        firefox_options = Options()
        firefox_options.add_argument('--headless')

        bplzdir = os.path.dirname(bplz.__file__)

        browser = webdriver.Firefox(options=firefox_options,
                                    executable_path=os.path.join(bplzdir, "geckodriver.exe"))
        browser.get(url)

        time.sleep(bufferTime)
        elem = browser.find_element_by_id("infos")
        html = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        readys = soup.find_all(id='ready')
        browser.close()
        browser.quit()
        filename = 1
        for ready in readys:
            filename += 1
            readyUrl = ready.contents[0].contents[3].attrs['href']
            readyName = ready.contents[0].contents[3].text

            req = request.Request(readyUrl)
            req.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/60.0.3080.5 Safari/537.36")

            response = request.urlopen(req, timeout=10)
            singleHtml = response.read().decode("utf-8")
            singleSoup = BeautifulSoup(singleHtml, 'html.parser')
            downloadPageUrl = "https://www.lanzous.com/" + singleSoup.find('iframe').attrs['src']

            self.downloadFile(firefox_options, bplzdir, bufferTime, downloadPageUrl, readyName, directory)

        while len([lists for lists in os.listdir(directory) if os.path.isfile(os.path.join(directory, lists))]) < len(
                readys) \
                or self.isExist(directory, ".part"):
            print("等待文件下载完成。。。。" +
                  str(len([lists for lists in os.listdir(directory) if
                           os.path.isfile(os.path.join(directory, lists))])) + "/" + str(len(readys)))
            time.sleep(bufferTime)
        print("下载完成。。。。")

        p = Popen("taskkill /IM firefox.exe /F", stdout=PIPE, stderr=STDOUT)

        return directory

    def downloadFile(self, firefox_options, bplzdir, bufferTime, downloadPageUrl, readyName, directory):

        browser1 = None
        for counter in range(5):
            try:
                profile = webdriver.FirefoxProfile()
                profile.set_preference('browser.download.dir', directory)
                profile.set_preference('browser.download.folderList', 2)
                profile.set_preference('browser.download.manager.showWhenStarting', False)
                profile.set_preference("browser.download.manager.showAlertOnComplete", False)
                profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                                       'application/octet-stream')  # 对应header里面的content-type

                browser1 = webdriver.Firefox(firefox_profile=profile, options=firefox_options,
                                             executable_path=os.path.join(bplzdir, "geckodriver.exe"))
                break
            except WebDriverException:
                # Cross platform
                PROCNAME = "geckodriver"
                for proc in psutil.process_iter():
                    # check whether the process name matches
                    if proc.name() == PROCNAME:
                        proc.kill()
                print("驱动错误，正在重试。。。")

        try:
            browser1.get(downloadPageUrl)
            print("获取下载链接成功：" + downloadPageUrl)
            time.sleep(bufferTime)
            browser1.find_element_by_tag_name('a').click()
            time.sleep(bufferTime)
            print("开始下载链接：" + downloadPageUrl)
            filesize = 0
            currentFilesize = 0
            success = False  # 判断任务是否完成
            for i in range(5):
                # 如果即存在文件又存在part文件，说明正在下载状态
                if (os.path.isfile(os.path.join(directory, readyName))
                    and os.path.isfile(os.path.join(directory, readyName + ".part"))) or \
                        (os.path.isfile(os.path.join(directory, quote(readyName)))
                         and os.path.isfile(os.path.join(directory, quote(readyName) + ".part"))):
                    if os.path.isfile(os.path.join(directory, readyName + ".part")):
                        currentFilesize = os.path.getsize(os.path.join(directory, readyName + ".part"))
                    else:
                        currentFilesize = os.path.getsize(os.path.join(directory, quote(readyName) + ".part"))

                    print("正在下载" + readyName + str(currentFilesize))
                    while currentFilesize > filesize:
                        time.sleep(bufferTime)
                        filesize = currentFilesize
                        print("正在下载" + readyName + str(currentFilesize))
                        if os.path.isfile(os.path.join(directory, readyName + ".part")) or \
                                os.path.isfile(os.path.join(directory, quote(readyName) + ".part")):
                            if os.path.isfile(os.path.join(directory, readyName + ".part")):
                                currentFilesize = os.path.getsize(os.path.join(directory, readyName + ".part"))
                            else:
                                currentFilesize = os.path.getsize(os.path.join(directory, quote(readyName) + ".part"))
                        else:
                            break
                # 如果只存在文件，不存在part文件，成功下载
                if (os.path.isfile(os.path.join(directory, readyName))
                    and not os.path.isfile(os.path.join(directory, readyName + ".part"))) or \
                        (os.path.isfile(os.path.join(directory, quote(readyName)))
                         and not os.path.isfile(os.path.join(directory, quote(readyName) + ".part"))):
                    print(readyName + "下载完毕")
                    if os.path.isfile(os.path.join(directory, quote(readyName))):
                        os.rename(os.path.join(directory, quote(readyName)), os.path.join(directory, readyName))
                    self.closeBrowser(browser1)
                    success = True
                    break
                # 如果既不存在文件，又不存在part文件，等待下载文件开始
                if (not os.path.isfile(os.path.join(directory, readyName))
                    and not os.path.isfile(os.path.join(directory, readyName + ".part"))) and \
                        (not os.path.isfile(os.path.join(directory, quote(readyName)))
                         and not os.path.isfile(os.path.join(directory, quote(readyName) + ".part"))):
                    print("等待" + readyName + "下载任务开始")
                    time.sleep(bufferTime)
            if not success:
                self.delFileCom(directory, readyName)
                print(readyName + "下载任务重启")
                self.closeBrowser(browser1)
                self.downloadFile(firefox_options, bplzdir, bufferTime, downloadPageUrl, readyName, directory)

        except:
            print("文件获取失败")
            self.closeBrowser(browser1)
            time.sleep(bufferTime)
            print("重启" + readyName + "下载任务")
            self.delFileCom(directory, readyName)
            self.downloadFile(firefox_options, bplzdir, bufferTime, downloadPageUrl, readyName, directory)

    def delFileCom(self, directory, readyName):
        if os.path.isfile(os.path.join(directory, quote(readyName))):
            self.delFile(directory, quote(readyName))
        else:
            self.delFile(directory, readyName)

    def delFile(self, directory, readyName):
        if os.path.exists(os.path.join(directory, readyName + ".part")):
            os.remove(os.path.join(directory, readyName + ".part"))
        if os.path.exists(os.path.join(directory, readyName)):
            os.remove(os.path.join(directory, readyName))

    def closeBrowser(self, browser1):
        browser1.close()
        browser1.quit()
        p = Popen("taskkill /IM firefox.exe /F", stdout=PIPE, stderr=STDOUT)

    def rename(self, directory):
        filelist = os.listdir(directory)
        zipfile = ""
        for i in range(len(filelist)):
            if filelist[i][-4:] == ".zip":
                zipfile = filelist[i]
                break

        for i in range(len(filelist)):
            # 设置旧文件名（就是路径+文件名）
            oldname = os.path.join(directory, filelist[i])  # os.sep添加系统分隔符
            # 设置新文件名
            if oldname != os.path.join(directory, zipfile):
                newname = os.path.join(directory, (zipfile[:-4] + "." + filelist[i])[:-4])
                os.rename(oldname, newname)  # 用os模块中的rename方法对文件改名
                print(oldname, '======>', newname)

    def zip_by_volume(self, file_path, block_size):
        """zip文件分卷压缩"""
        file_size = os.path.getsize(file_path)  # 文件字节数
        path, file_name = os.path.split(file_path)  # 除去文件名以外的path，文件名
        suffix = file_name.split('.')[-1]  # 文件后缀名
        # 添加到临时压缩文件
        zip_file = file_path + '.zip'
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.write(file_path, arcname=file_name)
        # 小于分卷尺寸则直接返回压缩文件路径
        if file_size <= block_size:
            return zip_file
        else:
            fp = open(zip_file, 'rb')
            count = file_size // block_size + 1
            # 创建分卷压缩文件的保存路径
            save_dir = path + os.sep + file_name + '_split'
            if os.path.exists(save_dir):
                from shutil import rmtree
                rmtree(save_dir)
            os.mkdir(save_dir)
            # 拆分压缩包为分卷文件
            for i in range(1, count + 1):
                _suffix = 'z{:0>2}'.format(i) if i != count else 'zip'
                name = save_dir + os.sep + file_name.replace(str(suffix), _suffix)
                f = open(name, 'wb+')
                if i == 1:
                    f.write(b'\x50\x4b\x07\x08')  # 添加分卷压缩header(4字节)
                    f.write(fp.read(block_size - 4))
                else:
                    f.write(fp.read(block_size))
            fp.close()
            os.remove(zip_file)  # 删除临时的 zip 文件
            return save_dir

    def zip_rename(self, save_dir):
        filelist = os.listdir(save_dir)
        for i in range(len(filelist)):
            if filelist[i][-3:] != "zip":
                oldname = os.path.join(save_dir, filelist[i])  # os.sep添加系统分隔符
                newname = os.path.join(save_dir, filelist[i][-3:] + ".rar")
                os.rename(oldname, newname)  # 用os模块中的rename方法对文件改名

    def main(self, argv):
        buftime = 2
        url = 'https://www.lanzous.com/b00tbv7wb'
        renamefolder = ""
        renamecreate = ""
        zipFile = ""
        volumeSize = 50
        onlyUrl = ""

        try:
            opts, args = getopt.getopt(argv, "hb:u:r:R:z:v:o:",
                                       ["buftime=", "url=", "renamefolder=", "renamecreate=", "zipfile=", "volumesize=",
                                        "onlyurl="])
        except getopt.GetoptError:
            print('bplz - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                  '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n' +
                  '-r 输入蓝奏云下载文件夹路径，单独使用\n' +
                  '-R 输入分卷压缩好的文件夹路径，单独使用\n' +
                  '-z 输入压缩文件全路径名\n' +
                  '-v 输入压缩卷大小（单位M），蓝奏云请输入50以下整数数字\n' +
                  '-o 输入蓝奏云文件夹下载目录，次下载不重命名')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                print('bplz - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                      '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n' +
                      '-r 输入蓝奏云下载文件夹路径，单独使用\n' +
                      '-R 输入分卷压缩好的文件夹路径，单独使用\n' +
                      '-z 输入压缩文件全路径名\n' +
                      '-v 输入压缩卷大小（单位M），蓝奏云请输入50以下整数数字\n' +
                      '-o 输入蓝奏云文件夹下载目录，次下载不重命名')
                sys.exit()
            elif opt in ("-b", "--buftime"):
                buftime = arg
            elif opt in ("-u", "--url"):
                url = arg
            elif opt in ("-r", "--renamefolder"):
                renamefolder = arg
            elif opt in ("-R", "--renamecreate"):
                renamecreate = arg
            elif opt in ("-z", "--zipfile"):
                zipFile = arg
            elif opt in ("-v", "--volumesize"):
                volumeSize = arg
            elif opt in ("-o", "--onlyurl"):
                onlyUrl = arg

        if len(opts) == 0:
            print('bplz - b 输入网页缓冲时间，单位秒，int类型,默认2秒\n' +
                  '-u 输入蓝奏云文件夹共享网址，注意网址不能有密码\n' +
                  '-r 输入蓝奏云下载文件夹路径，单独使用\n' +
                  '-R 输入分卷压缩好的文件夹路径，单独使用\n' +
                  '-z 输入压缩文件全路径名\n' +
                  '-v 输入压缩卷大小（单位M），蓝奏云请输入50以下整数数字\n' +
                  '-o 输入蓝奏云文件夹下载目录，次下载不重命名')
            sys.exit()

        if renamefolder != "":
            print('重命名蓝奏云下载文件夹为：' + renamefolder)
            self.rename(renamefolder)
        if renamecreate != "":
            print('重命分卷压缩好的文件夹路径为：' + renamecreate)
            self.zip_rename(renamecreate)
        elif zipFile != "":
            print('压缩文件为' + zipFile)
            print("分卷大小为" + str(volumeSize) + "M")
            save_folder = self.zip_by_volume(zipFile, int(volumeSize) * 1024 * 1024 if not isinstance(volumeSize,
                                                                                                      int) else volumeSize * 1024 * 1024)
            self.zip_rename(save_folder)
        elif onlyUrl != "":
            print('仅下载不重命名文件夹蓝奏云网络地址为：' + onlyUrl)
            directory = self.downloadRun(int(buftime), onlyUrl)
            print(directory)
        else:
            print('网页加载缓冲时间：' + str(buftime))
            print('蓝奏云文件夹共享网址：' + url)
            directory = self.downloadRun(int(buftime), url)
            print("开始修改文件名")
            self.rename(directory)
            print("文件下载完毕，放置位置为：" + directory)
            p = Popen("explorer " + directory, stdout=PIPE, stderr=STDOUT)
