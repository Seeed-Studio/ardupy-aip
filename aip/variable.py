
from datetime import date
from pip._internal.utils import appdirs
from pathlib import Path
import os
import stat

import json

mp_needful_file = ["/ardupycore/ArduPy/MicroPython/py/objmodule.c",
                   "/ardupycore/ArduPy/MicroPython/py/parse.c",
                   "/ardupycore/ArduPy/MicroPython/py/qstr.c"]


libarm_cortexM4lf_math_file = "/ardupycore/ArduPy/lib/libarm_cortexM4lf_math.a"


gcc_48 = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-gcc "
cpp_48 = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-g++ "
gcc_48_objcopy = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-objcopy "
gcc_48_size = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-size "

# {0}: board name
grove_ui_gcc_def = " -DARDUINO=10810 \
                    -DARDUINO_ARCH_SAMD \
                    -D{0} \
                    -DARDUPY_MODULE \
                    -DARM_MATH_CM4 \
                    -DENABLE_CACHE \
                    -DF_CPU=120000000L \
                    -DUSBCON \
                    -DUSB_CONFIG_POWER=100 -DUSB_MANUFACTURER=\"Seeed Studio\" -DUSB_PID=0x802D -DUSB_PRODUCT=\"Seeed Grove UI Wireles\" -DUSB_VID=0x2886 \
                    -DVARIANT_QSPI_BAUD_DEFAULT=50000000 -D__FPU_PRESENT -D__SAMD51P19A__ -D__SAMD51__ "

grove_ui_gcc_flag = " -mcpu=cortex-m4 -mthumb -c -g -w -std=gnu11 -ffunction-sections -fdata-sections -nostdlib -mfloat-abi=hard -mfpu=fpv4-sp-d16 -MMD -g -Wall -Werror -Wpointer-arith -Wuninitialized -Wno-unused-label -U_FORTIFY_SOURCE -Os"
grove_ui_cpp_flag = " -mcpu=cortex-m4 -mthumb -c -g -w -std=gnu++11 -ffunction-sections -fdata-sections -nostdlib -mfloat-abi=hard -mfpu=fpv4-sp-d16 -MMD -g -fno-rtti -fno-exceptions -fno-threadsafe-statics -g -Wall -Werror -Wpointer-arith -Wuninitialized -Wno-unused-label -std=gnu99 -U_FORTIFY_SOURCE -Os"


# {0}: ardupycore path
# {1}: output .o fils
# {2}: build temp dir
# {3}: board name
grove_ui_gcc_ld_flag = " -L{0}/Seeeduino/tools/CMSIS/4.5.0/CMSIS/Lib/GCC -Os -Wl,--gc-sections -save-temps -T {0}/ArduPy/boards/{3}/flash_with_bootloader.ld \
                        -Wl,-Map,{2}/firmware.map \
                        -Wl,--whole-archive {0}/ArduPy/lib/libmicropython.a -Wl,--no-whole-archive \
                        {1} -o {2}/Ardupy --specs=nano.specs --specs=nosys.specs -mcpu=cortex-m4 -mthumb -Wl,--cref -Wl,--check-sections -Wl,--gc-sections -Wl,--unresolved-symbols=report-all \
                        -Wl,--warn-common -Wl,--warn-section-align -Wl,--start-group -lm {0}/ArduPy/lib/libarm_cortexM4lf_math.a -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Wl,--end-group "

ardupycore_headers = ["/ardupycore/ArduPy",
                      "/ardupycore/ArduPy/MicroPython",
                      "/ardupycore/ArduPy/MicroPython/lib/lwip/src/include",
                      "/ardupycore/ArduPy/MicroPython/extmod/lwip-include",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino/Adafruit_TinyUSB_Core/tinyusb/src",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino/Adafruit_TinyUSB_Core",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/Wire",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/SPI",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/Adafruit_ZeroDMA",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/variants/grove_ui_wireless",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/core/arduino/USB",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/HID",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/USBHost/src",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/SAMD_AnalogCorrection/src",
                      "/ardupycore/Seeeduino/tools/CMSIS/4.5.0/CMSIS/Include",
                      "/ardupycore/Seeeduino/tools/CMSIS-Atmel/1.2.0/CMSIS/Device/ATMEL"]

board_headers = "/ardupycore/ArduPy/boards/"


grove_ui_flashParam = " -i -d --port=%s -U -i --offset=0x4000 -w -v %s -R "

# {0}: ardupy  path
# {1}: ardupy board path

micropython_CFLAGS = "-I. \
        -I{0} \
        -I{1} \
        -I{0}/MicroPython  \
        -Wall \
        -Werror \
        -Wpointer-arith \
        -Wuninitialized \
        -Wno-unused-label \
        -std=gnu99 \
        -U_FORTIFY_SOURCE \
        -Os \
        "
shell_commands = [
    'ls',
    'get',
    'put',
    'rm',
    'mkdir',
    'rmdir',
    'run',
    'repl',
    'reset',
    'scan',
    'bv',
]

def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# List of supported board USB IDs.  Each board is a tuple of unique USB vendor
# ID, USB product ID.
user_data_dir = appdirs.user_data_dir(appname="aip")

today = date.today()
with open(str(Path(user_data_dir, "package_seeeduino_ardupy_index_" + today.isoformat() + ".json")), 'r') as load_f:
    json_dict = json.load(load_f)
    BOARD_IDS = json_dict['board']
