

mp_needful_file = ["/ardupycore/ArduPy/MicroPython/py/objmodule.c", \
                    "/ardupycore/ArduPy/MicroPython/py/parse.c", \
                    "/ardupycore/ArduPy/MicroPython/py/qstr.c"]


libarm_cortexM4lf_math_file = "/ardupycore/ArduPy/lib/libarm_cortexM4lf_math.a"

grove_ui_ld_file = "/ardupycore/ArduPy/boards/grove_ui_m4/flash_with_bootloader.ld"

gcc_48 = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-gcc "
gcc_48_objcopy = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-objcopy "
gcc_48_size = "/ardupycore/Seeeduino/tools/arm-none-eabi-gcc/bin/arm-none-eabi-size "

grove_ui_gcc_def =  " -DARDUINO=10810 \
                    -DARDUINO_ARCH_SAMD \
                    -DARDUINO_GROVE_UI_WIRELESS \
                    -DARDUPY_MODULE \
                    -DARM_MATH_CM4 \
                    -DENABLE_CACHE \
                    -DF_CPU=120000000L \
                    -DSEEED_GROVE_UI_WIRELESS \
                    -DUSBCON \
                    -DUSB_CONFIG_POWER=100 -DUSB_MANUFACTURER=\"Seeed Studio\" -DUSB_PID=0x802D -DUSB_PRODUCT=\"Seeed Grove UI Wireles\" -DUSB_VID=0x2886 \
                    -DVARIANT_QSPI_BAUD_DEFAULT=50000000 -D__FPU_PRESENT -D__SAMD51P19A__ -D__SAMD51__ "

grove_ui_gcc_flag = " -mcpu=cortex-m4 -mthumb -c -g -w -std=gnu11 -ffunction-sections -fdata-sections -nostdlib -mfloat-abi=hard -mfpu=fpv4-sp-d16 -MMD -g -std=gnu11"

#{0}: ardupycore path
#{1}: output .o fils
#{2}: build temp dir
grove_ui_gcc_ld_flag = " -L{0}/Seeeduino/tools/CMSIS/4.5.0/CMSIS/Lib/GCC -Os -Wl,--gc-sections -save-temps -T {0}/ArduPy/boards/grove_ui_m4/flash_with_bootloader.ld \
                        -Wl,-Map,{2}/firmware.map \
                        -Wl,--whole-archive {0}/ArduPy/lib/libmicropython.a -Wl,--no-whole-archive \
                        {1} -o {2}/Ardupy --specs=nano.specs --specs=nosys.specs -mcpu=cortex-m4 -mthumb -Wl,--cref -Wl,--check-sections -Wl,--gc-sections -Wl,--unresolved-symbols=report-all \
                        -Wl,--warn-common -Wl,--warn-section-align -Wl,--start-group -lm {0}/ArduPy/lib/libarm_cortexM4lf_math.a -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Wl,--end-group "

grove_ui_ardupycore_headers =  "-I{0}/ardupycore/ArduPy/MicroPython \
                                -I{0}/ardupycore/ArduPy/boards/grove_ui_m4 \
                                -I{0}/ardupycore/ArduPy/MicroPython/lib/lwip/src/include \
                                -I{0}/ardupycore/ArduPy/MicroPython/extmod/lwip-include  \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/cores/arduino \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/cores/arduino/Adafruit_TinyUSB_Core/tinyusb/src \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/cores/arduino/Adafruit_TinyUSB_Core \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/Wire \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/SPI \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/Adafruit_ZeroDMA \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/variants/grove_ui_wireless \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/core/arduino/USB \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/HID \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/USBHost/src \
                                -I{0}/ardupycore/Seeeduino/hardware/samd/1.6.6/libraries/SAMD_AnalogCorrection/src \
                                -I{0}/ardupycore/Seeeduino/tools/CMSIS/4.5.0/CMSIS/Include \
                                -I{0}/ardupycore/Seeeduino/tools/CMSIS-Atmel/1.2.0/CMSIS/Device/ATMEL "


