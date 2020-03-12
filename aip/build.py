

from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import RequirementCommand
from pip._internal.cli.status_codes import SUCCESS,ERROR
from pip._internal.utils import appdirs
from pip._internal.cli import cmdoptions
from pip._internal.network.download import Downloader
from pip._internal.models.link import Link

from pip._internal.operations.prepare import (
    _copy_source_tree,
    _download_http_url,
    unpack_url,
)
import os
from .variable import *
from tempfile import *
import random
import shutil


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
            '-a', '--ailes',
            dest='files',
            action='store_true',
            default=False,
            help='Show the full list of installed files for each package.')

        self.parser.insert_option_group(0, self.cmd_opts)
        self.user_data_dir = appdirs.user_data_dir(appname = "aip")

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)
        self.srcfile = []

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
        gcc = self.user_data_dir+gcc_48
        gcc_def = grove_ui_gcc_def.replace("                    ", "")
        output_str = "   -o {0}   -c {1}"
        gcc_flag = grove_ui_gcc_flag
        gcc_cmd = gcc + gcc_def + self.headers + gcc_flag + output_str
        output_o = []


        #build all of source file
        for f in self.srcfile:
            randomstr = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba',8))
            #out = randomstr + os.path.basename(f)+".o"
            out =  os.path.join(outputdir, randomstr + os.path.basename(f)+".o")
            cmd  = gcc_cmd.format(out,f)
            print(cmd)
            output_o.append(out)
            os.system(cmd)
        
        gcc_ld_flag = grove_ui_gcc_ld_flag.format(self.user_data_dir+"/ardupycore"," ".join(output_o),outputdir).replace("                        ","")
        os.system(gcc+gcc_ld_flag)
        #print(" ".join(output_o))

    def downloadAll(self,session):
        link = Link("http://files.seeedstudio.com/ardupy/ardupy-core.zip")
        downloader = Downloader(session, progress_bar="on")
        ardupycoredir = self.user_data_dir+"/ardupycore"
        if not os.path.exists(ardupycoredir +"/Seeeduino") :
            try: 
                os.makedirs(ardupycoredir)
            except OSError as error: 
                print("Directory '%s was exists' "%ardupycoredir) 
            
            unpack_url(
                link,
                ardupycoredir,
                downloader=downloader,
                download_dir=None,
            )
        import sys
        if not os.path.exists(ardupycoredir +"/Seeeduino/tools/arm-none-eabi-gcc") :
            if sys.platform == "linux":
                link = Link("http://files.seeedstudio.com/arduino/tools/x86_64-pc-linux-gnu/gcc-arm-none-eabi-4.8.3-2014q1-linux64.tar.gz")
            if sys.platform == "win32":
                link = Link("http://files.seeedstudio.com/arduino/tools/i686-mingw32/gcc-arm-none-eabi-4.8.3-2014q1-windows.tar.gz")
            if sys.platform == "darwin":
                link = Link("http://files.seeedstudio.com/arduino/tools/x86_64-apple-darwin/gcc-arm-none-eabi-4.8.3-2014q1-mac.tar.gz")
            unpack_url(
                link,
                ardupycoredir +"/Seeeduino/tools/arm-none-eabi-gcc",
                downloader=downloader,
                download_dir=None,
            )           

    def run(self, options, args):
        session = self.get_default_session(options)
        deploydir = self.user_data_dir+"/deploy"
        builddir = mktemp()
        os.makedirs(builddir)
        
        if not os.path.exists(deploydir) :
            os.makedirs(deploydir)
        
        self.downloadAll(session)

        modules = os.listdir(self.user_data_dir +"/modules/") 
        self.headers = grove_ui_ardupycore_headers.format(self.user_data_dir,self.user_data_dir+"/modules/").replace("                                ", "")

        if modules :
            for m in modules :
                for f in self.fileEndWith(os.path.join(self.user_data_dir+"/modules/",m),'.cpp','.c'):
                    self.srcfile.append(f)
                self.headers = self.headers + " -I" + self.user_data_dir+"/modules/"+ m + " "

        for  mp_file in mp_needful_file:
            self.srcfile.append(self.user_data_dir+mp_file)


        print(self.srcfile)
        print(grove_ui_gcc_def.replace("                    ", ""))
        print(grove_ui_ardupycore_headers.format(self.user_data_dir).replace("                                ", ""))
        self.buildFarm(builddir)
        objcopy_cmd = self.user_data_dir + gcc_48_objcopy + "-O binary " + builddir + "/Ardupy " + deploydir + "/Ardupy.bin"
        os.system(objcopy_cmd)
        os.system(self.user_data_dir + gcc_48_size +" -A "+ builddir + "/Ardupy ")
        #delete builddir
        shutil.rmtree(builddir)
        return SUCCESS




