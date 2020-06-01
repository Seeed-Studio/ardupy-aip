
from datetime import date
from pip._internal.utils import appdirs
from pathlib import Path
from aip.logger import log
import os
import stat
import sys
import json

mp_needful_file = ["/ardupycore/ArduPy/MicroPython/py/objmodule.c",
                   "/ardupycore/ArduPy/MicroPython/py/parse.c",
                   "/ardupycore/ArduPy/MicroPython/py/qstr.c"]


libarm_cortexM4lf_math_file = "/ardupycore/ArduPy/lib/libarm_cortexM4lf_math.a"


arm_gcc = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-gcc "
arm_cpp = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-g++ "
arm_gcc_objcopy = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-objcopy "
arm_gcc_size = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-size "


# {0}: board name
# {1}: vid 
# {2}: pid
# {3}: usb product
gcc_defs = {
    "cortex-m4" : " -DARDUINO=10810 \
                    -DARDUINO_ARCH_SAMD \
                    -D{0} \
                    -DARDUPY_MODULE \
                    -DARM_MATH_CM4 \
                    -DENABLE_CACHE \
                    -DF_CPU=120000000L \
                    -DUSBCON \
                    -DLCD_SUPPORT \
                    -DUSB_CONFIG_POWER=100 -DUSB_MANUFACTURER=\"Seeed Studio\" -DUSB_PID={2} -DUSB_PRODUCT=\"{3}\" -DUSB_VID={1} \
                    -DVARIANT_QSPI_BAUD_DEFAULT=50000000 -D__FPU_PRESENT -D__SAMD51P19A__ -D__SAMD51__ ",
    "cortex-m0plus":" -DARDUINO=10810 \
            -DARDUINO_ARCH_SAMD \
            -DARDUPY_MODULE \
            -DF_CPU=48000000L \
            -D{0} \
            -DUSBCON \
            -DUSB_CONFIG_POWER=100 \
            -DUSB_MANUFACTURER=\"Seeed Studio\" -DUSB_PID={2} -DUSB_PRODUCT=\"{3}\" -DUSB_VID={1} \
            -D__SAMD21G18A__ -D__SAMD21__  "
}

gcc_flags = {
    "cortex-m4" : " -mcpu=cortex-m4 -mthumb -c -g -w -std=gnu11 -ffunction-sections -fdata-sections -nostdlib -mfloat-abi=hard -mfpu=fpv4-sp-d16 -MMD -g -Wall -Werror -Wpointer-arith -Wuninitialized -Wno-unused-label -U_FORTIFY_SOURCE -Os",
    "cortex-m0plus" : " -mcpu=cortex-m0plus -mthumb -c -g -Os -w -ffunction-sections -fdata-sections -nostdlib --param max-inline-insns-single=500 -MMD -DNDEBUG -DARM_MATH_CM0PLUS -std=gnu11 -g -Wall -Werror -Wpointer-arith -Wuninitialized -Wno-unused-label -std=gnu99 -U_FORTIFY_SOURCE -Os"
}

cpp_flags = {
    "cortex-m4" : " -mcpu=cortex-m4 -mthumb -c -g -w -std=gnu++11 -ffunction-sections -fdata-sections -nostdlib -mfloat-abi=hard -mfpu=fpv4-sp-d16 -MMD -g -fno-rtti -fno-exceptions -fno-threadsafe-statics -g -Wall -Werror -Wpointer-arith -Wuninitialized -Wno-unused-label -std=gnu99 -U_FORTIFY_SOURCE -Os",
    "cortex-m0plus" : " -mcpu=cortex-m0plus -mthumb -c -g -Os -w -ffunction-sections -fdata-sections -nostdlib --param max-inline-insns-single=500 -MMD -DNDEBUG -DARM_MATH_CM0PLUS -std=gnu++11 -fno-rtti -fno-exceptions -fno-threadsafe-statics -g"
}


# {0}: ardupycore path
# {1}: output .o fils
# {2}: build temp dir
# {3}: board name
ld_flags = {
    "cortex-m4" : "  -Os -Wl,--gc-sections -save-temps -T {0}/ArduPy/boards/{3}/flash_with_bootloader.ld \
                        -Wl,-Map,{2}/firmware.map \
                        -Wl,--whole-archive {0}/ArduPy/lib/libmicropython-cortexm4lf.a -Wl,--no-whole-archive \
                        {1} -o {2}/Ardupy --specs=nano.specs --specs=nosys.specs -mcpu=cortex-m4 -mthumb -Wl,--cref -Wl,--check-sections -Wl,--gc-sections -Wl,--unresolved-symbols=report-all \
                        -Wl,--warn-common -Wl,--warn-section-align -Wl,--start-group -lm {0}/ArduPy/lib/libarm_cortexM4lf_math.a -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Wl,--end-group ",

    "cortex-m0plus": " -Os -Wl,--gc-sections -save-temps -T {0}/ArduPy/boards/{3}/flash_with_bootloader.ld  \
                    -Wl,-Map,{2}/firmware.map \
                    -Wl,--whole-archive {0}/ArduPy/lib/libmicropython-cortexm0plus.a -Wl,--no-whole-archive  \
                    {1} -o {2}/Ardupy  --specs=nano.specs --specs=nosys.specs -mcpu=cortex-m0plus -mthumb -Wl,--cref -Wl,--check-sections -Wl,--gc-sections -Wl,--unresolved-symbols=report-all \
                    -Wl,--warn-common -Wl,--warn-section-align -Wl,--start-group -lm {0}/ArduPy/lib/libarm_cortexM0l_math.a -Wl,--end-group"
}

# {0} : ardupycore version
# (1) : variants name
samd_ardupycore_headers = ["/ardupycore/ArduPy",
                      "/ardupycore/ArduPy/MicroPython",
                      "/ardupycore/ArduPy/MicroPython/lib/lwip/src/include",
                      "/ardupycore/ArduPy/MicroPython/extmod/lwip-include",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino/Adafruit_TinyUSB_Core/tinyusb/src",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/cores/arduino/Adafruit_TinyUSB_Core",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/Wire",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/SPI",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/Adafruit_ZeroDMA",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/variants/{1}",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/core/arduino/USB",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/HID",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/USBHost/src",
                      "/ardupycore/Seeeduino/hardware/samd/{0}/libraries/SAMD_AnalogCorrection/src",
                      "/ardupycore/Seeeduino/tools/CMSIS/4.5.0/CMSIS/Include",
                      "/ardupycore/Seeeduino/tools/CMSIS-Atmel/1.2.1/CMSIS-Atmel/CMSIS/Device/ATMEL"]

board_headers = "/ardupycore/ArduPy/boards/"



flash_param = { 
    'Wio_terminal': ' -i -d --port=%s -U -i --offset=0x4000 -w -v %s -R ',
    'Seeeduino_XIAO' :  ' -i -d --port=%s -U -i  --offset=0x2000 -w -v %s -R '
}

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

def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# List of supported board USB IDs.  Each board is a tuple of unique USB vendor
# ID, USB product ID.
user_config_dir = appdirs.user_config_dir(appname="aip")
today = date.today()
package_seeeduino_ardupy_index_json = str(Path(user_config_dir, "package_seeeduino_ardupy_index_" + today.isoformat() + ".json"))
if os.path.exists(package_seeeduino_ardupy_index_json):
    with open(package_seeeduino_ardupy_index_json, 'r') as load_f:
        json_dict = json.load(load_f)
        BOARD_IDS = json_dict['board']
else:
    try:
        for file in os.listdir(user_config_dir):
            if "package_seeeduino_ardupy_index_" in file:
                package_seeeduino_ardupy_index_json = str(Path(user_config_dir, file))
                with open(package_seeeduino_ardupy_index_json, 'r') as load_f:
                    json_dict = json.load(load_f)
                    BOARD_IDS = json_dict['board']
                    break
    except Exception as e:
        log.error(e)
        log.error("The package_seeeduino_ardupy_index.json file is missing, execute aip to obtain it automatically")
        sys.exit(1)


