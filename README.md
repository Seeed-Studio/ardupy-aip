# ArduPy AIP [![Build Status](https://api.travis-ci.com/Seeed-Studio/ardupy-aip.svg?branch=master)](https://travis-ci.com/Seeed-Studio/ardupy-aip)
aip - ArduPy Integrated Platform is a utility to develop [ArduPy](https://github.com/Seeed-Studio/ArduPy) and  interact witch ArduPy board. It enables users to quickly get started with ardupy.

aip is meant to be a simple command line tool. You can customize your own ardupy firmware through it, without needing to know more details about ArduPy. And aip Integrated [mpfshell](https://github.com/wendlers/mpfshell), So you can also use it to interact with your ArduPy board, such as adding, deleting, checking and modifying files, and running repl.


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
| **aip** help | Help | **aip** help |
| **aip** board | Get board information  | **aip** board --scan |
|  **aip** build *-b <--board>*  | Build frimware |**aip** build -b wio_terminal   |
| **aip** flash *-p <--port>* | Flash frimware |**aip** flash |
| **aip** shell *-c "\<--cmd\>"* | Interact with the board |**aip** shell -c "repl"|

For more commands, see help.

