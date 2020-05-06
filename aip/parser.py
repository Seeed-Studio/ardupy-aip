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
import json
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
        
        self.boards = []
        self.packages = []
        #self.update_loacl_board_json()
        #self.update_loacl_library_json()
        self.parser_all_json()
        import platform
        sysstr = platform.system()
        if(sysstr =="Windows"):
            self.system = 'Windows'
        elif(sysstr == "Linux"):
            self.system = 'Linux'
        else:
            self.system = 'MacOS'

    def get_board_additional_url(self):
        url = self.cp.get("board", "additional_url")
        url = url.split(',')
        return url
    
    def add_board_additional_url(self, url):
        if re.match(r'^https?:/{2}\w.+$', url): # is a url?
            if(url.find('json') != -1):
                _url = self.cp.get("board", "additional_url")
                _url_list = _url.split(',') 
                if not (url in _url_list):
                    _url += ',' + url
                    self.cp.set('board', "additional_url", _url)
                    self.cp.write(self.config_file) #write to aip.conf
                    return True
                else:
                    log.error(url + " is existed.")
                    return False
            else:
                log.error(url + " is not a json file.")
                return False
        else:
            log.error(url + " is not a url.")
            return False
    


    def get_library_additional_url(self):
        url = self.cp.get("library", "additional_url")
        url = url.split(',')
        return url
    
    def add_library_additional_url(self, url):
        if re.match(r'^https?:/{2}\w.+$', url): # is a url?
            if(url.find('json') != -1):
                _url = self.cp.get("library", "additional_url")
                _url_list = _url.split(',') 
                if not (url in _url_list): # is existed?
                    _url += ',' + url
                    self.cp.set('library', "additional_url", _url)
                    self.cp.write(self.config_file) #write to aip.conf
                    return True
                else:
                    log.error(url + " is existed.")
                    return False
            else:
                log.error(url + " is not a json file.")
                return False
        else:
            log.error(url + " is not a url.")
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
    
    def parser_all_json(self): #parser all the json
        for path in os.listdir(self.user_config_dir):
            if path.find('json') != -1:
                try:
                    with open(str(Path(self.user_config_dir,path)), 'r') as load_f:
                        json_dict = json.load(load_f)
                        path = {'path': path}
                        package_id = 0  # package index in file
                        for _package in json_dict['packages']:
                            name = {'package': package_id}
                            platform_id = 0 # platform index in package
                            for _platform in _package['platforms']:
                                id = {'id': len(self.packages)}
                                platform = {'platform': platform_id}
                                arch = {'arch': _platform['architecture']}
                                package = {}
                                # Organize data and record
                                package.update(id)
                                package.update(name)
                                package.update(platform)
                                package.update(arch)
                                package.update(path)
                                self.packages.append(package)
                                for _board in _platform['board']:
                                    _board.update(id)
                                    self.boards.append(_board)
                                platform_id += 1
                            package_id +=1 
                except Exception as e:
                    log.error(e)

    def get_archiveFile_by_id(self, id):
        try:
            _package = self.packages[id]
            package_id = _package['package']
            platform_id = _package['platform']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                platform = json_dict['packages'][package_id]['platforms'][platform_id]
                archiveFile = {'package':json_dict['packages'][package_id]['name'], 'arch':platform['architecture'], 'version':platform['version'],  'url':platform['url'],'archiveFileName':platform['archiveFileName'], 'checksum':platform['checksum'], 'size':platform['size']}
                return archiveFile
        except Exception as e:
            log.error(e) 
        
        return None
    
    def get_archiveFile_by_board(self, board):
        id = board['id']
        return self.get_archiveFile_by_id(id)
    
    def get_board_by_name(self, name):
        for board in self.boards:
            if board['name'] == name:
                return board
        
        return None

    def get_id_by_name(self, name):
        for board in self.boards:
            if board['name'].replace(' ', '_') == name.replace(' ', '_'):
                return board['id']
        
        return None
    
    def get_toolsDependencies_by_id(self, id):
        try:
            _package = self.packages[id]
            package_id = _package['package']
            platform_id = _package['platform']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                platform = json_dict['packages'][package_id]['platforms'][platform_id]
                return platform['toolsDependencies']
        except Exception as e:
            log.error(e) 
        
        return None
    
    def get_toolsDependencies_url_by_id(self, id):
        dependencies = []
        try:
            _package = self.packages[id]
            package_id = _package['package']
            platform_id = _package['platform']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                platform = json_dict['packages'][package_id]['platforms'][platform_id]
                tools = json_dict['packages'][package_id]['tools']
                toolsDependencies = platform['toolsDependencies']
                for _toolsDependencies in toolsDependencies:
                    for _tools in tools:
                        if _tools['name'] == _toolsDependencies['name'] and _tools['version'] == _toolsDependencies['version']:
                            for _system in _tools['systems']:
                                if _system['host'] == self.system:
                                    _system.update({'name' : _tools['name']})
                                    _system.update({'version':  _tools['version']})
                                    dependencies.append(_system)
            return dependencies
        except Exception as e:
            log.error(e) 
        
        return None


parser = Parser()

def main():
    print(parser.get_id_by_name('wio terminal'))

if __name__ == '__main__':
    main()
    
        
