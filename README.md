# pyModbusServerGUI
Basic GUI to run a Modbus Server for testing purposes. Lets you set which coils respond as enabled and put values for input registers, also can set them to random values.

Makes use of pyModbusTCP for all the hard work: https://github.com/sourceperl/pyModbusTCP

GUI components use the dearpygui framework: https://github.com/hoffstadt/DearPyGui

Roadmap is to add in discrete inputs, analogue output registers, support updating the values being updated by a remote client (you can update them now but it won't be reflected in the GUI), then maybe allow for changing values over time.


# Usage
Needs Python 3.x for the GUI library, if you're having a problem running it then drop me a line and will see if I can work out what's up. Only tested on Mint 20 at this point. 

Requires pyModbusTCP and dearpygui to be installed with: 
`sudo pip install dearpygui pyModbusTCP`

Download all files, then run with:

`python pyModbusServerGUI-v0.1.py`

There should be a drop-down list of the available IP addresses on the machine to pick which the server will listen on. Standard Modbus/TCP port is 502 but that'd require running with root privileges. 

To set coils there are two options:
 - Use the Coils GUI to click on which coil addresses will be enabled or just use the randomise button. 
 - Type/paste in a comma separated list of values for the addresses of coils to enable.

To set input register values, type them into the relevant box on the grid, at the moment I've only enabled 1000 values otherwise the table gets enormous. Might add some kind of CSV import if needed.


Debug info gets dumped into the console so if it goes wrong then there may be some hints in the terminal you launched it from. 

License is Beerware

# Screenshots

![coil setting](https://github.com/unixhead/pyModbusServerGUI/blob/main/ss-coils-GUI.png?raw=true)

![register setting](https://github.com/unixhead/pyModbusServerGUI/blob/main/ss-input-registers.png?raw=true)
