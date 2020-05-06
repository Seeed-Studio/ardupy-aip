##
# The MIT License (MIT)
#
# Author: Hongtai Liu (lht856@foxmail.com)
#
# Copyright (C) 2020  Seeed Technology Co.,Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pip._internal.utils import appdirs
from configparser import ConfigParser
from aip.logger import log
import os
import re
from pathlib import Path
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class Parser(object):
    def __init__(self):
        self.user_config_dir = appdirs.user_config_dir(appname="aip")
        self.config_file_path = str(Path(self.user_config_dir, 'aip.conf'))
        if os.path.exists(self.config_file_path):
            self.config_file = open(self.config_file_path, 'r+')
            self.cp = ConfigParser()
            self.cp.read(self.config_file_path )
        else:   #if first time execute aip, create defalut config file.
            self.config_file = open(self.config_file_path, 'w+')
            self.cp = ConfigParser()
            self.cp.add_section('board')
            self.cp.set("board", "additional_url", "https://files.seeedstudio.com/ardupy/package_seeeduino_ardupy_index.json")
            self.cp.add_section('library')
            self.cp.set("library", "additional_url", "https://files.seeedstudio.com/ardupy/package_seeeduino_ardupy_index.json")
            self.cp.write(self.config_file)

    def get_board_additional_url(self):
        url = self.cp.get("board", "additional_url")
        url = url.split(',')
        return url
    
    def add_board_additional_url(self, url):
        if re.match(r'^https?:/{2}\w.+$', url): # is a url?
            if(url.find('json')):
                _url = self.cp.get("board", "additional_url")
                _url += ',' + url
                print(_url)
                self.cp.set('board', "additional_url", _url)
                self.cp.write(self.config_file) #write to aip.conf
                return True
            else:
                return False
        else:
            return False
    


    def get_library_additional_url(self):
        url = self.cp.get("library", "additional_url")
        url = url.split(',')
        return url
    
    def add_library_additional_url(self, url):
        if re.match(r'^https?:/{2}\w.+$', url): # is a url?
            if(url.find('json')):
                _url = self.cp.get("library", "additional_url")
                _url += ',' + url
                print(_url)
                self.cp.set('library', "additional_url", _url)
                self.cp.write(self.config_file) #write to aip.conf
                return True
            else:
                return False
        else:
            return False
    
    def update_loacl_board_json(self):
        log.info("update local board json...")
        for url in self.get_board_additional_url():
            url = url.strip()
            log.info(url)
            url_path = url.split('/')[len(url.split('/'))-1]
            try:
                urllib.request.urlretrieve(url,str(Path(self.user_config_dir, url_path)))
            except Exception as e:
                log.error(e)
                continue
            else:
                log.info("done!")
    
    def update_loacl_library_json(self):
        log.info("update local library json...")
        for url in self.get_library_additional_url():
            url = url.strip()
            log.info(url)
            url_path = url.split('/')[len(url.split('/'))-1]
            try:
                urllib.request.urlretrieve(url,str(Path(self.user_config_dir, url_path)))
            except Exception as e:
                log.error(e)
                continue
            else:
                log.info("done!")
        


def main():
    parser = Parser()
    print(parser.get_library_additional_url())

if __name__ == '__main__':
    main()
    
        
