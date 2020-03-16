# chose an implementation, depending on os
#~ if sys.platform == 'cli':
#~ else:
import os
if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
#~ elif os.name == 'java':
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))

# List of supported board USB IDs.  Each board is a tuple of unique USB vendor
# ID, USB product ID.
BOARD_IDS = \
    [{
        "name": "wio terminal",
        "appcation": ("2886", "802D"),
        "bootloader": ("2886", "002D"),
    },{
        "name": "Seeeduino XIAO",
        "appcation": ("2886", "802E"),
        "bootloader": ("2886", "002E"),
    }]


class SerialUtils(object):
    def __init__(self):
        super().__init__()
        
    
    def getAllPortInfo(self):
        return comports(include_links=False)
    
    def getAvailableBoard(self):
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            print(hwid)
            if ii != -1:
                for b in  BOARD_IDS:
                    (vid, pid) = b["appcation"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        print(port,desc, hwid)
                        return port,desc, hwid, False
                    (vid, pid) = b["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        print(port,desc, hwid)
                        return port,desc, hwid, True

        return ("None","None","None",False)
        
    def isBootloaderStatus(self):

        return True

if __name__ == '__main__':
    ser = SerialUtils()
    for info in ser.getAllPortInfo():
        port, desc, hwid = info
        print("port: {}, desc: {}, hwid: {}".format(port, desc, hwid))
    print(ser.getAvailableBoard())
