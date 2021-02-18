
# The MIT License (MIT)
#
# Author: Baozhu Zuo (zuobaozhu@gmail.com)
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

from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import RequirementCommand
from pip._internal.cli.status_codes import SUCCESS, ERROR
from pip._internal.cli import cmdoptions
from pip._internal.network.download import Downloader
from pip._internal.models.link import Link
import shutil

from pip._internal.operations.prepare import (
    unpack_url,
)
import os
from aip.variable import *
from tempfile import *
from aip.utils import SerialUtils
from aip.utils import dealGenericOptions
from aip.logger import log
from aip.parser import parser
import random
import shutil
import time
import sys
from pathlib import Path
import re


class buildCommand(RequirementCommand):
    """
    Build ArduPy Firmware contains the libraries you installed and the basic ArduPy features.
    """
    name = 'build'
    usage = """
      %prog [options] <args> ..."""
    summary = "Build ArduPy Firmware contains the libraries you installed and the basic ArduPy features."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(buildCommand, self).__init__(*args, **kw)

        self.parser.insert_option_group(0, self.cmd_opts)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )
        self.serial = SerialUtils()
        self.parser.insert_option_group(0, index_opts)
        self.srcfile = []
        self.headers = ""
        self.headerlist = []
        self.buildParm = ""
        self.gcc = ""
        self.cpp = ""
        self.objcopy = ""
        self.sizetool = ""
        self.ld = ""
        self.board_id = -1
        self.gcc_cmd = ""
        self.cpp_cmd = ""
        self.objcopy_cmd = ""
        self.sizetool_cmd = ""
        self.ld_cmd = ""
        self._verbose = False

    def doVerbose(self, info):
        if self.verbose == True:
            print(info)
        else:
            sys.stdout.write(".....")
            sys.stdout.flush()

    # get arm gcc

    def initBoard(self):
        self.buildParm = parser.get_build_pram_by_id(self.board_id)
        buildParm = self.buildParm
        self.gcc = str(Path(parser.get_tool_dir_by_id(
            self.board_id), buildParm['tool'], buildParm['version'], "bin", buildParm['CC']))
        self.cpp = str(Path(parser.get_tool_dir_by_id(
            self.board_id), buildParm['tool'], buildParm['version'], "bin", buildParm['CXX']))
        self.objcopy = str(Path(parser.get_tool_dir_by_id(
            self.board_id), buildParm['tool'], buildParm['version'], "bin", buildParm['OBJCOPY']))
        self.sizetool = str(Path(parser.get_tool_dir_by_id(
            self.board_id), buildParm['tool'], buildParm['version'], "bin", buildParm['SIZETOOL']))
        self.buildParm = parser.get_build_pram_by_id(self.board_id)

    # build firmware
    def buildFirmware(self, outputdir):
        buildParm = self.buildParm
        product = parser.boards[self.board_id]["name"]
        pid = parser.boards[self.board_id]["hwids"]["application"][0]
        vid = parser.boards[self.board_id]["hwids"]["application"][1]
        common_flags = " " + buildParm["CFLAGS"] + " " + parser.boards[self.board_id]["BOARDFLAGS"] + " " + buildParm["ARDUINOCFLAGS"].format(arduinocore=parser.get_arduino_dir_by_id(
            self.board_id)) + " " + buildParm["USBFLAGS"].format(product, pid, vid) + " " + buildParm["TOOLCFLAGS"].format(parser.get_tool_dir_by_id(self.board_id)) + " " + buildParm["EXTRACFLAGS"]
        gcc_flags = common_flags + " " + buildParm["CCFLAGS"]
        cpp_flags = common_flags + " " + buildParm["CXXFLAGS"]
        output_str = " -o {0}   -c {1}"
        self.gcc_cmd = self.gcc + " " + gcc_flags + \
            " " + self.headers + " " + output_str
        self.cpp_cmd = self.cpp + " " + cpp_flags + \
            " " + self.headers + " " + output_str
        output_o = []
        # build all of source file
        for f in self.srcfile:
            randomstr = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 8))
            #out = randomstr + os.path.basename(f)+".o"
            out = os.path.join(outputdir, randomstr + os.path.basename(f)+".o")
            (path, filename) = os.path.split(f)
            if filename[-2:] == ".c":
                cmd = self.gcc_cmd.format(out, f)
                self.doVerbose(cmd)
                output_o.append(out)
                os.system(cmd)
            else:
                cmd = self.cpp_cmd.format(out, f)
                self.doVerbose(cmd)
                output_o.append(out)
                os.system(cmd)

        self.ld_cmd = self.gcc + " -L{0} ".format(parser.get_ardupy_board_by_id(self.board_id)) + " " + buildParm["TOOLLDFLAGS"].format(parser.get_tool_dir_by_id(
            self.board_id)) + " " + buildParm["EXTRALDFLAGS"] + " " + buildParm["LINKFLAGS"].format(parser.get_ardupy_board_by_id(self.board_id), " ".join(output_o), outputdir)
        self.doVerbose(self.ld_cmd)
        os.system(self.ld_cmd)

    def endWith(self, s, *endstring):
        array = map(s.endswith, endstring)
        if True in array:
            return True
        else:
            return False

    def fileEndWith(self, p, *endstring):
        all_file = []
        wants_files = []

        for r, d, f in os.walk(p):
            if r.find('.git') == -1:
                for item in f:
                    all_file.append(os.path.join(r, item))
        for i in all_file:
            if self.endWith(i, endstring):
                wants_files.append(i)
        return wants_files

    # generated Init file
    def generatedInitfile(self, outputdir):

        init_header = """
#include <stdint.h>

#include "py/obj.h"
#include "py/runtime.h"

        """
        fix_body = """

STATIC const mp_rom_map_elem_t arduino_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__),                          MP_ROM_QSTR(MP_QSTR_arduino) },
        """
        init_tail = """
};

STATIC MP_DEFINE_CONST_DICT(arduino_module_globals, arduino_module_globals_table);

const mp_obj_module_t mp_module_arduino = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&arduino_module_globals,
};        
        """
        mp_obj_type_string = []

        for ff in self.srcfile:
            (path, filename) = os.path.split(ff)
            if filename[0:11] == "mod_ardupy_":
                with open(ff, 'r') as f:
                    mp_obj_type_string.append(''.join([line for line in f.readlines(
                    ) if re.match(r'const mp_obj_type_t ', line)])[20: -5])

        initFile = open(str(Path(outputdir, "__init__.c")), "w")
        initFile.write(init_header)
        for ss in mp_obj_type_string:
            initFile.write("extern const mp_obj_type_t  {};\n\t".format(ss))

        initFile.write(fix_body)
        for ss in mp_obj_type_string:
            initFile.write(
                '{{ MP_ROM_QSTR(MP_QSTR_{0}),                         MP_ROM_PTR(&{1}) }},\n\t'.format(ss[:-5], ss))
        initFile.write(init_tail)
        initFile.close()
        # os.system("cat "+str(Path(outputdir,"__init__.c")))
        self.srcfile.append(str(Path(outputdir, "__init__.c")))

    def generatedQstrdefs(self, outputdir):
        ardupydir = parser.get_ardupy_dir_by_id(self.board_id)
        sys.path.append(str(Path(ardupydir, "MicroPython", "py")))
        # import makemoduledefs
        import makeqstrdata
        import makeqstrdefs
        # import makeversionhdr
        genhdr = str(Path(outputdir+"/genhdr"))
        os.makedirs(genhdr)
        extern_mp_src = []

        # makeversionhdr.make_version_header(str(Path(genhdr,"mpversion.h")))
        shutil.copyfile(str(Path(parser.get_gender_dir_by_id(
            self.board_id), "mpversion.h")), str(Path(genhdr, "mpversion.h")))
        shutil.copyfile(str(Path(parser.get_gender_dir_by_id(
            self.board_id), "moduledefs.h")), str(Path(genhdr, "moduledefs.h")))

        mp_generate_flag = " -I. -I{0} -I{1}".format(parser.get_ardupy_dir_by_id(
            self.board_id), parser.get_ardupy_board_by_id(self.board_id))

        buildParm = self.buildParm
        micropython_CFLAGS = buildParm["MICROPYTHONCFLAGS"].format(
            parser.get_ardupy_dir_by_id(self.board_id))

        mp_generate_flag = " {} {} ".format(
            mp_generate_flag, micropython_CFLAGS)

        # remove cpp files
        # todo； only scan file start wirh "mod_ardupy_"
        for f in self.srcfile:
            if f[-3:] == "cpp" or f[-2:] == "cc":
                continue
            if f.find("objmodule.c") != -1 or \
                f.find("parse.c") != -1 or \
                    f.find("qstr.c") != -1:
                continue
            extern_mp_src.append(f)
        self.doVerbose(extern_mp_src)
        gen_i_last = self.gcc + " -E -DARDUPY_MODULE -DNO_QSTR " + mp_generate_flag + " ".join(extern_mp_src) + \
            "  " + str(Path(parser.get_ardupy_dir_by_id(self.board_id), "mpconfigport.h")) + \
            " > " + str(Path(genhdr, "qstr.i.last"))
        self.doVerbose(gen_i_last)
        os.system(gen_i_last)

        import io

        class Args:
            pass
        args = Args()
        args.input_filename = str(Path(genhdr, "qstr.i.last"))
        args.output_dir = str(Path(genhdr, "qstr"))
        args.output_file = str(Path(genhdr, "qstrdefs.collected.h"))
        try:
            os.makedirs(args.output_dir)
        except OSError:
            pass

        makeqstrdefs.args = args
        with io.open(args.input_filename, encoding='utf-8') as infile:
            makeqstrdefs.process_file(infile)

        makeqstrdefs.cat_together()
        qcfgs, qstrs = makeqstrdata.parse_input_headers([str(Path(parser.get_gender_dir_by_id(self.board_id), "qstrdefs.preprocessed.h")),
                                                         str(Path(genhdr, "qstrdefs.collected.h"))])

        qstrdefs_generated_h = open(
            str(Path(genhdr, "qstrdefs.generated.h")), "w")

        # get config variables
        cfg_bytes_len = int(qcfgs['BYTES_IN_LEN'])
        cfg_bytes_hash = int(qcfgs['BYTES_IN_HASH'])

        # self.doVerbose out the starter of the generated C header file
        qstrdefs_generated_h.writelines(
            '// This file was automatically generated by makeqstrdata.py\n')
        qstrdefs_generated_h.writelines('\n')

        # add NULL qstr with no hash or data
        qstrdefs_generated_h.writelines('QDEF(MP_QSTR_NULL, (const byte*)"%s%s" "")\n' % (
            '\\x00' * cfg_bytes_hash, '\\x00' * cfg_bytes_len))

        # go through each qstr and self.doVerbose it out
        for order, ident, qstr in sorted(qstrs.values(), key=lambda x: x[0]):
            qbytes = makeqstrdata.make_bytes(
                cfg_bytes_len, cfg_bytes_hash, qstr)
            qstrdefs_generated_h.writelines(
                'QDEF(MP_QSTR_%s, %s)\n' % (ident, qbytes))
        qstrdefs_generated_h.close()

        # os.system("cp "+ str(Path(genhdr,"qstrdefs.generated.h"))+" /tmp")
        self.headerlist.append(str(Path(genhdr)))

        return genhdr

    def downloadAll(self, session):
        archiveFile = parser.get_archiveFile_by_id(self.board_id)
        downloader = Downloader(session, progress_bar="on")
        ardupycoredir = parser.get_core_dir_by_id(self.board_id)
        if not os.path.exists(ardupycoredir):
            log.info('Downloading ' +
                        archiveFile['archiveFileName'] + '...')
            try:
                unpack_url(
                    Link(archiveFile['url']),
                    ardupycoredir,
                    downloader,
                    download_dir=None,
                )
            except Exception as e:
                    log.error(e)
                    os.remove(ardupycoredir)
                    sys.exit(1)
            except Exception as e:
                log.error(e)
                os.remove(ardupycoredir)
                sys.exit(1)

        toolsDependencies = parser.get_toolsDependencies_url_by_id(
            self.board_id)
        toolsdir = parser.get_tool_dir_by_id(self.board_id)
        for tool in toolsDependencies:
            tooldir = str(Path(toolsdir, tool['name'],  tool['version']))
            if not os.path.exists(tooldir):
                log.info('Downloading ' +
                         tool['name'] + '@' + tool['version'] + '...')
                try:
                    unpack_url(
                        Link(tool['url']),
                        tooldir,
                        downloader,
                        download_dir=None,
                    )
                except Exception as e:
                    log.error(e)
                    os.remove(tooldir)
                    sys.exit(1)

    def run(self, options, args):

        if options.board == "":
            port, desc, hwid, isbootloader = self.serial.getAvailableBoard()
            if port != None:
                _board = self.serial.getBoardByPort(port)
                if _board != "":
                    self.board = _board[0]
            else:
                log.warning(
                    "please plug in a ArduPy Board or specify the board to build!")
                print("<usage>    aip build [--board=<board>] ")
                return
        else:
            self.board = options.board

        self.board_id = self.serial.getBoardIdByName(self.board)

        if self.board_id == -1:
            log.error("Unable to find information about '" + self.board + "'")
            return ERROR

        self.verbose = options.verbose

        self.initBoard()
        seesion = self.get_default_session(options)
        self.downloadAll(seesion)

        # setup deploy dir
        deploydir = parser.get_deploy_dir_by_id(self.board_id)

        if not os.path.exists(deploydir):
            os.makedirs(deploydir)
        # create build dir, This folder will be deleted after compilation
        builddir = mktemp()
        os.makedirs(builddir)

        log.info("|---------------" + " Building Firmware for " +
                 self.board + "---------------|")

        arduinodir = parser.get_arduino_dir_by_id(self.board_id)
        arduinocoredir = str(Path(arduinodir, "cores", "arduino"))

        # Converts the header file to the absolute path of the current system
        # 1 append Arduino Core PATH
        self.headerlist.append(arduinocoredir)
        for file in os.listdir(arduinocoredir):
            file_path = str(Path(arduinocoredir, file))
            if os.path.isdir(file_path):
                self.headerlist.append(file_path)

        # 2 append Arduino variants PATH
        self.headerlist.append(parser.get_variant_dir_by_id(self.board_id))

        # 3 append Arduino library PATH
        librariesdir = str(Path(arduinodir, "libraries"))

        for library in os.listdir(librariesdir):
            library_path = str(Path(librariesdir, library))
            self.headerlist.append(library_path)
            if(os.path.exists(str(Path(library_path, "src")))):
                self.headerlist.append(str(Path(library_path, "src")))

        # 4 append Ardupy core PATH
        self.headerlist.append(parser.get_ardupy_dir_by_id(self.board_id))
        self.headerlist.append(parser.get_ardupy_board_by_id(self.board_id))
        self.headerlist.append(
            str(Path(parser.get_ardupy_dir_by_id(self.board_id), "MicroPython")))

        # 5 append moudules PATh
        moduledir = str(Path(parser.user_config_dir, "modules"))
        if not os.path.exists(moduledir):
            os.makedirs(moduledir)
        modules = os.listdir(moduledir)
        if modules:
            for m in modules:
                # Gets the source files for all modules
                for f in self.fileEndWith(os.path.join(str(Path(moduledir, m))), '.cpp', '.c'):
                    self.srcfile.append(str(Path(f)))
                # Sets the root directory of the module to be where the header file is found
                for r, d, f in os.walk(str(Path(moduledir, m))):
                    if r.find('.git') == -1 and r.find("examples") == -1:
                        self.headerlist.append(r)

        # 6 Convert the necessary files in ardupycore into the absolute path of the system.
        self.srcfile.append(str(Path(parser.get_ardupy_dir_by_id(
            self.board_id), "MicroPython", "py", "objmodule.c")))
        self.srcfile.append(str(Path(parser.get_ardupy_dir_by_id(
            self.board_id), "MicroPython", "py", "parse.c")))
        self.srcfile.append(str(Path(parser.get_ardupy_dir_by_id(
            self.board_id), "MicroPython", "py", "qstr.c")))

        # 7 generatrd Init file for binding
        self.generatedInitfile(builddir)

        # 8 Convert to the required format for GCC
        self.generatedQstrdefs(builddir)

        # 9 append build temp dir
        self.headerlist.append(str(Path(builddir)))

        # 10 inform headers headerlist
        self.headers = "-I" + " -I".join(self.headerlist)

        # 11 build firmware
        self.buildFirmware(builddir)

        # 12 remove the old firmware
        firmware_path = str(Path(str(deploydir), "Ardupy.bin"))
        if os.path.exists(firmware_path):
            os.remove(firmware_path)

        # 13 convert elf to bin
        self.objcopy_cmd = self.objcopy + " -O binary " \
            + str(Path(builddir + "/Ardupy")) + " " \
            + firmware_path

        self.doVerbose(self.objcopy_cmd)
        os.system(self.objcopy_cmd)

        # 14 print information
        self.sizetool_cmd = self.sizetool + \
            " -A " + str(Path(builddir + "/Ardupy"))
        print("")
        os.system(self.sizetool_cmd)

        # 15 print information
        # delete build dir
        shutil.rmtree(builddir)

        if os.path.exists(firmware_path):
            log.info('Firmware path: ' + firmware_path)
            log.info('Usage:\n\r    aip flash')
        else:
            raise Exception(print('compile error'))

        return SUCCESS
