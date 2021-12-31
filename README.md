# pyModbusServerGUI
Basic GUI to run a Modbus Server for testing purposes

Makes use of pyModbusTCP for all the hard work: https://github.com/sourceperl/pyModbusTCP

GUI components use the dearpygui framework: https://github.com/hoffstadt/DearPyGui


# Usage
Needs Python 3.x for the GUI library, if you're having a problem running it then drop me a line and will see if I can work out what's up. Only tested on Mint 20 at this point. 

Requires pyModbusTCP and dearpygui to be installed with: 
`sudo pip install dearpygui pyModbusTCP`

Download all files, then run with:

`python pyModbusServerGUI-v0.1.py`

Debug info gets dumped into the console so if it goes wrong then there may be some hints in the terminal you launched it from. 

License is Beerware

# Screenshots

![coil setting](https://github.com/unixhead/pyModbusServerGUI/blob/main/ss-input-registers.png?raw=true)

![register setting](https://github.com/unixhead/pyModbusServerGUI/blob/main/ss-input-registers.png?raw=true)
