# ArduPy AIP [![Build Status](https://api.travis-ci.com/Seeed-Studio/ardupy-aip.svg?branch=master)](https://travis-ci.com/Seeed-Studio/ardupy-aip)
aip - ArduPy Integrated Platform is a utility to develop [ArduPy](https://github.com/Seeed-Studio/ArduPy) and interact
with an ArduPy board. It enables users to quickly get started with ArduPy.

aip is meant to be a simple command line tool. You can customize your own ardupy firmware through it, without needing
to know more details about ArduPy. aip is also integrated with [mpfshell](https://github.com/wendlers/mpfshell),
so you can also use it to interact with your ArduPy board, such as adding, deleting, checking and modifying files, and running a REPL.


### Installation

- To install the latest release from PyPI:
```
      sudo pip install ardupy-aip
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
|  **aip** build *-b <--board>*  | Build firmware |**aip** build -b wio_terminal   |
| **aip** flash *-p <--port>* | Flash firmware |**aip** flash |
| **aip** shell *-c "\<--cmd\>"* | Interact with the board |**aip** shell -c "repl"|

For more commands, see help.
