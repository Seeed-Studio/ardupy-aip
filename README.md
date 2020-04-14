# ArduPy AIP
aip is a utility to develop [ArduPy](https://github.com/Seeed-Studio/ArduPy) and  interact witch ArduPy board. It enables users to quickly get started with ardupy.

aip is meant to be a simple command line tool. You can customize your own ardupy firmware through it, without needing to know more details about ArduPy. You can also use it to interact with your development board, such as adding, deleting, checking and modifying files, and running repl.


### Installation

- To install the latest release from PyPi:
```
      sudo pip install aip
```
- From Source
Clone this repository:
```
      git clone https://github.com/Seeed-Studio/ardupy-aip
```

- To install for Python 3, execute the following:
```
      pip3 install -U -r .
```

### Usage

| cmd  | function|  Example|
| ---- | ---- | ---- |
| **aip** help | help | aip help |
|  **aip** build *-b <--board>*  | build frimware |aip build -b wio_terminal   |
| **aip** flash *-p <--port>* | flash frimware |aip flash |
| **aip** rshell *--cmd repl* | open repl |**aip** rshell *-cmd repl* |

For more commands, see help.

