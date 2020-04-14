
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
    _copy_source_tree,
    _download_http_url,
    unpack_url,
)
import os
from aip.variable import *
from tempfile import *
import random
import shutil
import sys
from pathlib import Path
import re


class buildCommand(RequirementCommand):
    """
    Show information about one or more installed packages.

    The output is in RFC-compliant mail header format.
    """
    name = 'build'
    usage = """
      %prog [options] <package> ..."""
    summary = "build all of package"
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        super(buildCommand, self).__init__(*args, **kw)

        self.cmd_opts.add_option(
            '-b', '--board',
            dest='board',
            action='store',
            default="",
            help='The name of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)
        self.srcfile = []
        self.header = ""
        self.board = "wio_terminal"
        self.arduinoCoreVersion = "1.7.1"
        self.gcc = str(Path(user_data_dir+gcc_48))
        self.cpp = str(Path(user_data_dir+cpp_48))
        self.headerlist = []

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

    def buildFarm(self, outputdir):
        gcc_def = grove_ui_gcc_def.format(
            self.board.upper()).replace("                    ", "")
        output_str = "   -o {0}   -c {1}"
        gcc_flag = grove_ui_gcc_flag
        gcc_cmd = self.gcc + gcc_def + self.headers + gcc_flag + output_str
        cpp_cmd = self.cpp + gcc_def + self.headers + grove_ui_cpp_flag + output_str
        output_o = []
        # build all of source file
        for f in self.srcfile:
            randomstr = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 8))
            #out = randomstr + os.path.basename(f)+".o"
            out = os.path.join(outputdir, randomstr + os.path.basename(f)+".o")
            (path, filename) = os.path.split(f)
            if filename[-2:] == ".c":
                cmd = gcc_cmd.format(out, f)
                print(cmd)
                output_o.append(out)
                os.system(cmd)
            else:
                cmd = cpp_cmd.format(out, f)
                print(cmd)
                output_o.append(out)
                os.system(cmd)

        gcc_ld_flag = grove_ui_gcc_ld_flag.format(user_data_dir+"/ardupycore", " ".join(
            output_o), outputdir, self.board).replace("                        ", "")
        print(self.gcc+gcc_ld_flag)
        os.system(self.gcc+gcc_ld_flag)

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

        initFile = open(Path(outputdir, "__init__.c"), "w")
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
        sys.path.append(
            str(Path(user_data_dir+"/ardupycore/ArduPy/MicroPython/py")))
        # import makemoduledefs
        import makeqstrdata
        import makeqstrdefs
        # import makeversionhdr
        genhdr = Path(outputdir+"/genhdr")
        os.makedirs(genhdr)
        extern_mp_src = []

        # makeversionhdr.make_version_header(str(Path(genhdr,"mpversion.h")))
        shutil.copyfile(str(Path(
            user_data_dir+"/ardupycore/Seeeduino/tools/genhdr/mpversion.h")), str(Path(genhdr, "mpversion.h")))
        shutil.copyfile(str(Path(user_data_dir+"/ardupycore/Seeeduino/tools/genhdr/moduledefs.h")),
                        str(Path(genhdr, "moduledefs.h")))

        mp_generate_flag = micropython_CFLAGS.format(str(Path(user_data_dir+"/ardupycore/ArduPy")),
                                                     str(Path(user_data_dir+"/ardupycore/ArduPy/boards/"+self.board)))

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

        gen_i_last = self.gcc + "-E -DARDUPY_MODULE -DNO_QSTR " + mp_generate_flag + " ".join(extern_mp_src) + \
            "  " + str(Path(user_data_dir+"/ardupycore/ArduPy/boards/"+self.board+"/mpconfigport.h")) + \
            " > " + str(Path(genhdr, "qstr.i.last"))
        print(gen_i_last)
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
        qcfgs, qstrs = makeqstrdata.parse_input_headers([str(Path(user_data_dir+"/ardupycore/Seeeduino/tools/genhdr/qstrdefs.preprocessed.h")),
                                                         str(Path(genhdr, "qstrdefs.collected.h"))])

        qstrdefs_generated_h = open(Path(genhdr, "qstrdefs.generated.h"), "w")

        # get config variables
        cfg_bytes_len = int(qcfgs['BYTES_IN_LEN'])
        cfg_bytes_hash = int(qcfgs['BYTES_IN_HASH'])

        # print out the starter of the generated C header file
        qstrdefs_generated_h.writelines(
            '// This file was automatically generated by makeqstrdata.py\n')
        qstrdefs_generated_h.writelines('\n')

        # add NULL qstr with no hash or data
        qstrdefs_generated_h.writelines('QDEF(MP_QSTR_NULL, (const byte*)"%s%s" "")\n' % (
            '\\x00' * cfg_bytes_hash, '\\x00' * cfg_bytes_len))

        # go through each qstr and print it out
        for order, ident, qstr in sorted(qstrs.values(), key=lambda x: x[0]):
            qbytes = makeqstrdata.make_bytes(
                cfg_bytes_len, cfg_bytes_hash, qstr)
            qstrdefs_generated_h.writelines(
                'QDEF(MP_QSTR_%s, %s)\n' % (ident, qbytes))
        qstrdefs_generated_h.close()

        # os.system("cp "+ str(Path(genhdr,"qstrdefs.generated.h"))+" /tmp")
        self.headerlist.append(str(outputdir))

        return genhdr

    def downloadAll(self, session):
        link = Link("http://files.seeedstudio.com/ardupy/ardupy-core.zip")
        downloader = Downloader(session, progress_bar="on")
        ardupycoredir = user_data_dir+"/ardupycore"
        if not os.path.exists(ardupycoredir + "/ArduPy"):
            try:
                os.makedirs(ardupycoredir)
            except OSError as error:
                print("Directory '%s was exists' " % ardupycoredir)
                print(error)
                
            unpack_url(
                link,
                ardupycoredir,
                downloader=downloader,
                download_dir=None,
            )
        if not os.path.exists(ardupycoredir + "/Seeeduino/tools/arm-none-eabi-gcc"):
            if sys.platform == "linux":
                link = Link(
                    "http://files.seeedstudio.com/arduino/tools/x86_64-pc-linux-gnu/gcc-arm-none-eabi-4.8.3-2014q1-linux64.tar.gz")
            if sys.platform == "win32":
                link = Link(
                    "http://files.seeedstudio.com/arduino/tools/i686-mingw32/gcc-arm-none-eabi-4.8.3-2014q1-windows.tar.gz")
            if sys.platform == "darwin":
                link = Link(
                    "http://files.seeedstudio.com/arduino/tools/x86_64-apple-darwin/gcc-arm-none-eabi-4.8.3-2014q1-mac.tar.gz")
            unpack_url(
                link,
                ardupycoredir + "/Seeeduino/tools/arm-none-eabi-gcc",
                downloader=downloader,
                download_dir=None,
            )

    def clean(self):
        ardupycoredir = user_data_dir+"/ardupycore/ArduPy"
        if os.path.exists(ardupycoredir):
            try:
                shutil.rmtree(ardupycoredir)
            except OSError as error:
                print("Directory '%s remove failed' " % ardupycoredir)
                print(error)

    def run(self, options, args):
        if 'clean' in args:
            self.clean()
            return SUCCESS

        if options.board != "":
            self.board = options.board

        session = self.get_default_session(options)
        
        # setup deploy dir
        deploydir = Path(user_data_dir, "deploy")
        if not os.path.exists(deploydir):
            os.makedirs(deploydir)
        # create build dir, This folder will be deleted after compilation
        builddir = mktemp()
        os.makedirs(builddir)

        self.downloadAll(session)

        # Converts the header file to the absolute path of the current system
        for h in ardupycore_headers:
            # add Arduino Core version
            if h[0:35] == "/ardupycore/Seeeduino/hardware/samd":
                h = h.format(self.arduinoCoreVersion)
            self.headerlist.append(str(Path(user_data_dir+h)))
        self.headerlist.append(
            str(Path(user_data_dir+board_headers+self.board)))

        # setup ardupy modules dir
        moduledir = Path(user_data_dir, "modules")
        if not os.path.exists(moduledir):
            os.makedirs(moduledir)
        modules = os.listdir(moduledir)
        if modules:
            for m in modules:
                # Gets the source files for all modules
                for f in self.fileEndWith(os.path.join(user_data_dir+"/modules/", m), '.cpp', '.c'):
                    self.srcfile.append(str(Path(f)))
                # Sets the root directory of the module to be where the header file is found
                for r, d, f in os.walk(str(Path(user_data_dir+"/modules/" + m))):
                    if r.find('.git') == -1 and r.find("examples") == -1:
                        self.headerlist.append(r)

        # Convert the necessary files in ardupycore into the absolute path of the system.
        for mp_file in mp_needful_file:
            self.srcfile.append(str(Path(user_data_dir+mp_file)))

        self.generatedInitfile(builddir)

        # Convert to the required format for GCC
        self.generatedQstrdefs(builddir)
        self.headers = "-I" + " -I".join(self.headerlist)

        # Compile all source files
        self.buildFarm(builddir)

        # Convert ELF files to binary files
        objcopy_cmd = str(Path(user_data_dir + gcc_48_objcopy)) + "-O binary " \
            + str(Path(builddir + "/Ardupy")) + " " \
            + str(Path(str(deploydir) + "/Ardupy.bin"))
        print(objcopy_cmd)
        os.system(objcopy_cmd)

        # Print size information
        os.system(str(Path(user_data_dir + gcc_48_size)) +
                  " -A " + str(Path(builddir + "/Ardupy")))

        print('\033[32mFirmware path: '+str(Path(str(deploydir) + "/Ardupy.bin")) + '\033[0m')
        print('\033[32mUsage:\n\r    aip flash ' + str(Path(str(deploydir) + "/Ardupy.bin")) + '\033[0m')
        # delete builddir
        shutil.rmtree(builddir)
        return SUCCESS
