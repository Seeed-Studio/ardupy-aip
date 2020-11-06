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

from configparser import ConfigParser
from pathlib import Path
import urllib.request
import sys
from datetime import date, datetime
import os
import re
import json
import ssl
import shutil
import stat
ssl._create_default_https_context = ssl._create_unverified_context

from pip._internal.utils import appdirs
from aip.logger import log

def get_platform():
    import platform
    _platform = platform.platform()
    _os = 'undifined'
    if _platform.find('Windows') >= 0:
        _os = 'i686-mingw32'
    elif _platform.find('Linux') >= 0:
        if _platform.find('arm') >= 0:
            _os = 'arm-linux-gnueabihf'
        elif _platform.find('x86_64') >= 0:
            _os = 'x86_64-pc-linux-gnu'
        elif _platform.find('i686') >= 0:
            _os = 'i686-pc-linux-gnu'
        elif _platform.find('aarch64') >= 0: 
            _os = 'aarch64-linux-gnu'
    elif _platform.find('Darwin') >= 0 or _platform.find('macOS') >= 0:
            _os = 'x86_64-apple-darwin'
    
    return _os

class Parser(object):
    def __init__(self):
        self.user_config_dir = appdirs.user_config_dir(appname="aip")
        self.config_file_path = str(Path(self.user_config_dir, 'aip.conf'))
        if os.path.exists(self.config_file_path):
            self.config_file = open(self.config_file_path, 'r+')
            self.cp = ConfigParser()
            self.cp.read(self.config_file_path)
            self.check_board_version()
        else:   #if first time execute aip, create defalut config file.
            if not os.path.exists(self.user_config_dir):
                os.mkdir(self.user_config_dir)
            if(os.path.exists(str(Path(self.user_config_dir, "ardupycore")))):
                shutil.rmtree(str(Path(self.user_config_dir, "ardupycore")))

            for path in os.listdir(self.user_config_dir):
                if path.find('json') != -1:
                    os.remove(str(Path(self.user_config_dir, path)))

            self.config_file = open(self.config_file_path, 'w+')
            self.cp = ConfigParser()
            self.cp.add_section('board')
            self.cp.set("board", "additional_url", "http://files.seeedstudio.com/ardupy/package_new_seeeduino_ardupy_index.json")
            self.cp.add_section('library')
            self.cp.set("library", "additional_url", "")
            self.cp.write(self.config_file)
            self.config_file.close()
            self.update_loacl_board_json()
            #self.update_loacl_library_json()
        
        self.boards = []
        self.packages = []
       
        self.parser_all_json()
        self.system = get_platform()
    
    def check_board_version(self):
        time = self.cp.get('board', 'update time')
        if time != str(date.today().isoformat()):
            self.update_loacl_board_json()

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
        self.config_file = open(self.config_file_path, 'r+')
        self.cp = ConfigParser()
        self.cp.read(self.config_file_path)
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
                self.cp.set("board", 'update time', str(date.today().isoformat()))
                self.cp.write(self.config_file)
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

    def get_core_id(self, arg):
        _core = arg.split(":")
        if len(_core) < 2:
            return None 
        package = _core[0]
        platform = _core[1]
        version = None
        if len(_core) >= 3:
            version = _core[2]
      
        for _package in self.packages:
            if package == _package['package_name'] and platform == _package['arch'] and (version == None or version == _package["version"]):
                return _package["id"]
        
        return None
    
    def parser_all_json(self): #parser all the json
        for path in os.listdir(self.user_config_dir):
            if path.find('json') and path.find('package') != -1:
                try:
                    with open(str(Path(self.user_config_dir,path)), 'r') as load_f:
                        json_dict = json.load(load_f)
                        path = {'path': path}
                        package_id = 0  # package index in file
                        for _package in json_dict['packages']:
                            package = {'package': package_id}
                            package_name = {'package_name': _package['name']}
                            platform_id = 0 # platform index in package
                            for _platform in _package['platforms']:
                                id = {'id': len(self.packages)}
                                platform = {'platform': platform_id}
                                platform_name = {'platform_name': _platform['name']}
                                version =  {'version': _platform['version']}
                                arch = {'arch': _platform['architecture']}
                                packages = {}
                                # Organize data and record
                                packages.update(id)
                                packages.update(package)
                                packages.update(package_name)
                                packages.update(platform)
                                packages.update(platform_name)
                                packages.update(version)
                                packages.update(package)
                                packages.update(arch)
                                packages.update(path)
                                self.packages.append(packages)
                                for _board in _platform['board']:
                                    _package_id = {'package_id': packages['id']}
                                    _board_id = {'id': len(self.boards)}
                                    _board.update(_package_id)
                                    _board.update(_board_id)
                                    self.boards.append(_board)
                                platform_id += 1
                            package_id +=1 
                except Exception as e:
                    log.error(e)

    def get_archiveFile_by_id(self, id):
        try:
            _package_id = self.boards[id]['package_id']
            _package = self.packages[_package_id]
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
    
    def get_toolsDependencies_by_id(self, board_id):
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
            package_id = _package['package']
            platform_id = _package['platform']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                platform = json_dict['packages'][package_id]['platforms'][platform_id]
                return platform['toolsDependencies']
        except Exception as e:
            log.error(e) 
        
        return None
    
    def get_toolsDependencies_url_by_id(self, board_id):
        dependencies = []
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
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

    def get_ardupycore_dir_by_package_id(self, package_id):

        try:
            _package = self.packages[package_id]
            package_id = _package['package']
            platform_id = _package['platform']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                platform = json_dict['packages'][package_id]['platforms'][platform_id]
                archiveFile = {'package':json_dict['packages'][package_id]['name'], 'arch':platform['architecture'], 'version':platform['version'],  'url':platform['url'],'archiveFileName':platform['archiveFileName'], 'checksum':platform['checksum'], 'size':platform['size']}
                ardupycoredir = str(Path(self.user_config_dir, 'ardupycore', archiveFile['package'], 'hardware', archiveFile['arch'], archiveFile['version']))
                return ardupycoredir
        except Exception as e:
            log.error(e) 
        
        return None
    
    def get_core_dir_by_id(self, board_id):
        archiveFile = self.get_archiveFile_by_id(board_id)
        ardupycoredir =  ardupycoredir = str(Path(self.user_config_dir, 'ardupycore', archiveFile['package'], 'hardware', archiveFile['arch'], archiveFile['version'], 'core'))
        return  ardupycoredir
    
    def get_arduino_dir_by_id(self, board_id):
        ardupycoredir = self.get_core_dir_by_id(board_id)
        arduinocoredir = str(Path(ardupycoredir, "Arduino"))
        return  arduinocoredir
    

    def get_ardupy_dir_by_id(self, board_id):
        ardupycoredir = self.get_core_dir_by_id(board_id)
        ardupydir = str(Path(ardupycoredir, "ArduPy"))
        return  ardupydir

    def get_ardupy_board_by_id(self, board_id):
        ardupydir = self.get_ardupy_dir_by_id(board_id)
        board = self.boards[board_id]["name"].replace(' ', '_')
        ardupy_board = str(Path(ardupydir, "boards", board))
        return ardupy_board

    
    def get_variant_dir_by_id(self, board_id):
        arduinocoredir = self.get_arduino_dir_by_id(board_id)
        variant = self.boards[board_id]["variant"]
        variantdir = str(Path(arduinocoredir, "variants", variant))
        return variantdir
    
    def get_gender_dir_by_id(self, board_id):
        ardupy_board = self.get_ardupy_dir_by_id(board_id)
        board = self.boards[board_id]["name"].replace(' ', '_')
        genhdrdir = str(Path(ardupy_board, 'genhdr', board))
        return genhdrdir
    
    def get_tool_dir_by_id(self, board_id):
        archiveFile = self.get_archiveFile_by_id(board_id)
        tooldir = str(Path(self.user_config_dir, 'ardupycore', archiveFile['package'], 'tools'))
        return tooldir

    def get_flash_tool_by_id(self, board_id):
        flash_tool_dir = ""
        tool_dir = self.get_tool_dir_by_id(board_id)
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
            _flash = self.boards[board_id]['architecture']
         
            package_id = _package['package']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                flashs = json_dict['packages'][package_id]['flash']
                for flash in flashs:
                    if(flash['name'] == _flash):
                        flash_tool_dir = str(Path(tool_dir, flash['tools'], flash['version']))
                        break
        except Exception as e:
            log.error(e) 
    
        if flash_tool_dir == "":
            log.error("Can't find flash tool, please check package_index.json!")

        return flash_tool_dir

    def get_flash_command_by_id(self, board_id, port, firmware):
        flash_command = ""
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
            _flash = self.boards[board_id]['architecture']
            package_id = _package['package']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                flashs = json_dict['packages'][package_id]['flash']
                for flash in flashs:
                    if(flash['name'] == _flash):
                        if self.system == "i686-mingw32":
                            tool = flash['tools']+'.exe'
                        else: 
                            tool = flash['tools']
                        flash_command = tool + flash['command']
                        flash_command = flash_command.format(str(port), str(firmware))
        except Exception as e:
            log.error(e) 
        
        if flash_command == "":
            log.error("Can't find flash tool depency, please check package_index.json!")

        return flash_command

    def get_flash_isTouch_by_id(self, board_id):
        isTouch = False
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
            _flash = self.boards[board_id]['architecture']
            package_id = _package['package']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                flashs = json_dict['packages'][package_id]['flash']
                for flash in flashs:
                    isTouch = flash["isTouch"]
        except Exception as e:
            log.error(e) 
        
        return isTouch

    def get_deploy_dir_by_id(self, board_id):
        board = self.boards[board_id]['name'].replace(' ', '_')
        deploy_dir = str(Path(self.user_config_dir, 'deploy', board))
        return deploy_dir
    
    def get_build_pram_by_id(self, board_id):
        try:
            _package_id = self.boards[board_id]['package_id']
            _package = self.packages[_package_id]
            _build = self.boards[board_id]['architecture']
            package_id = _package['package']
            with open(str(Path(self.user_config_dir,_package['path'])), 'r') as load_f:
                json_dict = json.load(load_f)
                builds = json_dict['packages'][package_id]['build']
                for build in builds:
                    if(build['name'] == _build):
                        return build
        except Exception as e:
            log.error(e) 
        log.error("Can't find build pram")
        return ""
    

parser = Parser()

def main():
    #parser.update_loacl_board_json()
    print(parser.get_ardupy_board_by_id(0))

if __name__ == '__main__':
    main()
    
        
