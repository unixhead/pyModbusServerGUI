
# pyModbusServerGUI
# Original source: https://github.com/unixhead/pyModbusServerGUI

# Beerware license

# Uses PyModbusTCP for all the hard work
# https://github.com/sourceperl/pyModbusTCP
#
# Includes specific version of pyModbusTCP as the one installed by pip doesn't seem to include the new databank structure at time of writing

#
# Needs dearpygui and pymodbusTCP, run:
# pip install dearpygui pyModbusTCP
#
# Not sure if you need pyModbusTCP installed given I've bundled it, but it's that way on my test machine. 
# Presumably at some point pip will install the new version and I won't need to bundle it.
#


from pyModbusTCP.server import ModbusServer, ModbusServerDataBank
import time

class modbusServer:
    running = False
    address = "127.0.0.1"
    port = 10502
    serverObj = False # server object from pyModbusTCP library
    dataBank = False

    def __init__(self):
        # databank object is used by pyModbusTCP to store the response values
        self.dataBank = ModbusServerDataBank()
        

    def startServer(self):
        if self.checkRunning() == True:
            return True

        self.serverObj = ModbusServer(host=self.address, port=self.port, no_block=True, data_bank=self.dataBank)
        self.serverObj.start()
        
        # Wait 2 seconds for everything to settle and then check our status
        time.sleep(2)
        return self.checkRunning()

    def stopServer(self):
        self.serverObj.stop()
        time.sleep(2) # wait 2 seconds for it to settle
        if self.checkRunning() == False:
            self.serverObj = False
            return True
        else:
            return False


    def setCoilBits(self, coilList):
        self.debugLog("setCoilBits with array size: " + str(len(coilList)))
        #self.debugLog("array: " + str(coilList))

        if self.checkRunning() == False:
            self.debugLog("set coils called without live server")
            return False

        #self.data_hdl.dataBank.set_coils(0, coilList)
        self.serverObj.data_hdl.write_coils(0, coilList, "None")


    def setRegisterValues(self, registerList, type="input"):
        self.debugLog("setRegisterValues with array size: " + str(len(registerList)))
        if self.checkRunning() == False:
            self.debugLog("set registers called without live server")
            return False

        if type == "output":
            self.serverObj.data_hdl.data_bank.set_holding_registers(40000, registerList)
        else:
            self.serverObj.data_hdl.data_bank.set_input_registers(30000, registerList)



    def clearRegisterValues(self, type="input"):
        if type == "output":
            self.serverObj.data_hdl.data_bank.set_holding_registers(40000, [0] * 9999)
        else:
            self.serverObj.data_hdl.data_bank.set_input_registers(30000, [0] * 9999)


    def clearCoilBits(self):
        self.serverObj.data_hdl.write_coils(0, [0] * 9999, "None")

    def setAddress(self, data):
        self.address = data

    def setPort(self, data):
        self.port = int(data)


    def checkRunning(self): 
        if self.serverObj == False:
            self.debugLog("Server not running")
            return False

        if self.serverObj.is_run == True:
            self.running = True
            self.debugLog("Server Running")
            return True
        else:
            self.running = False
            self.debugLog("Server not running")
            return False


    def debugLog(self,data = None):
        print(data)
        




#
# Code to draw the GUI
#
# Supported ranges:
# 1-9999 - discrete output coils R/W - binary
# 10001 - 19999 - discrete input contacts R/O - binary
# 30001 - 39999 - analog input registers - R/O - 16 bit int
# 40001 - 49999 - analog output holding registers - R/W - 16 bit int
#

import dearpygui.dearpygui as dpg
import random


modbusServer = modbusServer()

NUMCOILS = 1000 # number of coils we allow user to configure in the GUI, if this is too large then the display is unusable
COILSPERROW = 40 # how many coil tickboxes to display in each table row
MAXCOILROWS = int(NUMCOILS/COILSPERROW)
MAXCOILS = 9999 # maximum size of coil list that can be imported
coilList = [0] * MAXCOILS


NUMREGISTERS = 1000 # number of registers that can be entered in the GUI
REGISTERSPERROW = 20 # how many to display on one row of the table
MAXREGISTERROWS = int(NUMREGISTERS/REGISTERSPERROW)
MAXREGISTERS = 9999
registerList = [0] * MAXREGISTERS
outputRegisterList = [0] * MAXREGISTERS

dpg.create_context()

#print any debug info text into console
def debugLog(text):
    print(str(text))


def startModbusServer(sender, app_data, user_data):
    modbusServer.setAddress(dpg.get_value("serverAddress"))
    modbusServer.setPort(dpg.get_value("serverPort"))

    if modbusServer.startServer():
        dpg.configure_item("serverStatus", default_value="Running")
        dpg.bind_item_theme("serverStatus", green_bg_theme)        
    else:
        dpg.configure_item("serverStatus", default_value="Not Running")
        dpg.bind_item_theme("serverStatus", red_bg_theme)



def stopModbusServer(sender, app_data, user_data):
    if modbusServer.checkRunning(): # if it's not running then don't do anything
        if modbusServer.stopServer(): # try to stop the server
            dpg.configure_item("serverStatus", default_value="Not Running")
            dpg.bind_item_theme("serverStatus", red_bg_theme)
        else:
            dpg.configure_item("serverStatus", default_value="Error stopping server")

  
def checkModbusServer(sender, app_data):
    modbusServer.checkRunning()



def coilClicked(sender, app_data, user_data):   
    debugLog(f"coilClicked - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global coilList

    if (user_data < COILSPERROW):
        row = 0
        col = user_data
    else:
        if ((user_data % COILSPERROW) == 0):
            col = COILSPERROW
            row = int(user_data/COILSPERROW)-1
        else:
            col = user_data % COILSPERROW
            row = int(user_data/COILSPERROW)


    #debugLog("row: " + str(row) + " col: " + str(col))
    if (app_data == True): #the box was ticked
        dpg.highlight_table_cell(coil_table_id, row, col, [0, 230, 0, 100])
        coilList[user_data] = 1;       
    else: # the box was unticked from previously being selected
        dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])
        coilList[user_data] = 0;
        
    #debugLog("coilClicked:" + str(coilList)   )

    modbusServer.setCoilBits(coilList)



def randomiseCoils(sender, app_data, user_data):
    debugLog(f"randomiseCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global coilList

    for i in range(1,MAXCOILROWS*COILSPERROW):
        if (i < COILSPERROW):
            row = 0
            col = i
        else:
            if ((i % COILSPERROW) == 0):
                col = COILSPERROW
                row = int(i/COILSPERROW)-1
            else:
                col = i % COILSPERROW
                row = int(i/COILSPERROW)

        if (random.randint(0, 100) > 50):
            dpg.highlight_table_cell(coil_table_id, row, col, [0, 230, 0, 100])
            coilList[i] = 1;
            #print("coils" + str(i))
            #no idea why these sometimes fail, catch the exception and ignore it as it doesn't really impact much
            try:
                dpg.configure_item("coils" + str(i), default_value=True)
            except:
                debugLog("failed to update coil value to true for:" + str(i))
        else:
            try:
                dpg.configure_item("coils" + str(i), default_value=False)
                dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])
            except:
                debugLog("failed to update coil value to false for:" + str(i))
            coilList[i] = 0;

    #debugLog("RandomiseCoils array:" + str(coilList))
    modbusServer.setCoilBits(coilList)




def clearCoils(sender, app_data, user_data):
    debugLog(f"clearCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global coilList

    for i in range(1,MAXCOILROWS*COILSPERROW):
        if (i < COILSPERROW):
            row = 0
            col = i
        else:
            if ((i % COILSPERROW) == 0):
                col = COILSPERROW
                row = int(i/COILSPERROW)-1
            else:
                col = i % COILSPERROW
                row = int(i/COILSPERROW)

        dpg.configure_item("coils" + str(i), default_value=False)
        dpg.highlight_table_cell(coil_table_id, row, col, [230, 0, 0, 100])
    
    coilList = False
    coilList = [0] * MAXCOILS

    #debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearCoilBits()



def setManualCoils(sender, app_data, user_data):
    debugLog(f"setManualCoils - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    # clear out the GUI options incase they were set before
    clearCoils("uNF", "uNF", "uNF")
    global coilList

    #convert list of numbers to correct format (list of size 9999 that's either 0 or 1)
    #assume values are between 0-9999 for the moment

    origList = dpg.get_value("coilValueInputText")
    if len(origList) < 1: # no data provided
        dpg.configure_item("coilValueStatusText", default_value="Invalid List Format - Must be CSV")
        dpg.bind_item_theme("coilValueStatusText", red_bg_theme)
    else:
        # no format checking - possible future amendment
        origList = dpg.get_value("coilValueInputText").split(",")
        coilList = [0] * MAXCOILS

        for i in range(0,len(origList)):
            
            if origList[i] != ",":
                #debugLog("setting value for " + origList[i])
                val = int(origList[i])
                coilList[val] = 1

        modbusServer.setCoilBits(coilList)
        dpg.configure_item("coilValueStatusText", default_value="List Set")
        dpg.bind_item_theme("coilValueStatusText", green_bg_theme)
        



def randomiseRegisters(sender, app_data, user_data):
    debugLog(f"randomiseRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global registerList
    
    for i in range(1,NUMREGISTERS):
        randRegisterValue = random.randint(0,65535)
        registerList[i] = randRegisterValue
        try: 
            dpg.configure_item("registers" + str(i), default_value=randRegisterValue) #set table entry to zero
        except: # not sure why this sometimes fails
            debugLog("failed to update GUI field: registers" + str(i))
    modbusServer.setRegisterValues(registerList)


def clearRegisters(sender, app_data, user_data):
    debugLog(f"clearRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global registerList

    for i in range(1,NUMREGISTERS):
        dpg.configure_item("registers" + str(i), default_value="0")
    
    registerList = False
    registerList = [0] * MAXREGISTERS

    #debugLog("ClearCoils: " + str(coilList))
    modbusServer.clearRegisterValues("input")

def registerTextChanged(sender, app_data, user_data):
    debugLog(f"registerTextChangedsender - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    startModbusServer("uNF","uNF","uNF")
    global registerList 
    if len(app_data) == 0:
        app_data = 0
        dpg.configure_item(sender, default_value="0")

    registerList[user_data] = app_data;  
    #debugLog("registerTextChanged: " + str(registerList))
    modbusServer.setRegisterValues(registerList, "input")



def randomiseOutputRegisters(sender, app_data, user_data):
        debugLog(f"randomiseOutputRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
        startModbusServer("uNF","uNF","uNF")
        global outputRegisterList
        
        for i in range(1,NUMREGISTERS):
            randRegisterValue = random.randint(0,65535)
            outputRegisterList[i] = randRegisterValue
            try: 
                dpg.configure_item("outputregisters" + str(i), default_value=randRegisterValue) 
            except: # not sure why this sometimes fails
                debugLog("failed to update GUI field: outputregisters" + str(i))
        modbusServer.setRegisterValues(registerList, "output")




def clearOutputRegisters(sender, app_data, user_data):
        debugLog(f"clearOutputRegisters - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
        startModbusServer("uNF","uNF","uNF")
        global outputRegisterList

        for i in range(1,NUMREGISTERS):
            dpg.configure_item("outputregisters" + str(i), default_value="0")
        
        outputRegisterList = False
        outputRegisterList = [0] * MAXREGISTERS

        #debugLog("ClearCoils: " + str(coilList))
        modbusServer.clearRegisterValues("output")


   



def outputRegisterTextChanged(sender, app_data, user_data):
        debugLog(f"outputRegisterTextChanged - sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
        startModbusServer("uNF","uNF","uNF")
        global outputRegisterList 
        if len(app_data) == 0:
            app_data = 0
            dpg.configure_item(sender, default_value="0")
            
        outputRegisterList[user_data] = app_data;  
        modbusServer.setRegisterValues(outputRegisterList, "output")


def _log(sender, app_data, user_data):
        print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

# Uses open Sans font from https://github.com/adobe-fonts/source-sans
# License for this font: https://github.com/adobe-fonts/source-sans/blob/release/LICENSE.md
with dpg.font_registry():
    default_font = dpg.add_font("SourceSans3-Regular.otf", 20)




with dpg.theme() as green_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 153, 0), category=dpg.mvThemeCat_Core)
        

with dpg.theme() as red_bg_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (230, 0, 0), category=dpg.mvThemeCat_Core)

       



with dpg.window(tag="Primary Window", width=800):

    dpg.bind_font(default_font)
    dpg.add_text("Modbus/TCP Server Address:", tag="serverText")
    
    #get list of all available IPs and offer to user in a dropdown list
    from netifaces import interfaces, ifaddresses, AF_INET
    ip_list = []
    for interface in interfaces():
        debugLog("Address Found: " + str(ifaddresses(interface)))
        for link in ifaddresses(interface).get(AF_INET, ()):
            ip_list.append(link['addr'])


    dpg.add_combo((ip_list),default_value=ip_list[0], tag="serverAddress",  width=250, indent=200)
    serverAddressGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverText", parent=serverAddressGroup)
    dpg.move_item("serverAddress", parent=serverAddressGroup)
    
    dpg.add_text("Port:", tag="serverPortText")
    dpg.add_input_text(default_value="10502", tag="serverPort", width=100, indent=200)
    
    serverPortGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverPortText", parent=serverPortGroup)
    dpg.move_item("serverPort", parent=serverPortGroup)


    dpg.add_button(label="Start Server", callback=startModbusServer, tag="startServerButton")
    dpg.add_button(label="Stop Server", callback=stopModbusServer, tag="stopServerButton")
    dpg.add_button(label="Check Server", callback=checkModbusServer, tag="checkServerButton")
    dpg.add_text("Status:", tag="serverStatusText")
    dpg.add_input_text(default_value="Not Running", tag="serverStatus" , width=150, readonly=True, indent=200)
    serverStatusGroup = dpg.add_group(horizontal=True)
    dpg.move_item("serverStatusText", parent=serverStatusGroup)
    dpg.move_item("serverStatus", parent=serverStatusGroup)
    dpg.move_item("startServerButton", parent=serverStatusGroup)
    dpg.move_item("stopServerButton", parent=serverStatusGroup)
    dpg.move_item("checkServerButton", parent=serverStatusGroup)



    # 1-9999 - discrete output coils R/W - binary
    # At the moment it is R/O, the backend server library may let clients write values but they won't be reflected in the GUI
    with dpg.collapsing_header(label="Discrete Output Coil Values GUI"):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _coil_child_window:

            dpg.add_button(label="Randomise Coil Values", callback=randomiseCoils, tag="randomiseCoilsButton")
            dpg.add_button(label="Clear Coil Values", callback=clearCoils, tag="clearCoilsButton")
            coilValueGroup = dpg.add_group(horizontal=True)
            dpg.move_item("randomiseCoilsButton", parent=coilValueGroup)
            dpg.move_item("clearCoilsButton", parent=coilValueGroup)

            
            with dpg.table(tag="coilsTable", header_row=True, row_background=False,
                                borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit, borders_innerV=True,
                                borders_outerV=True, delay_search=True,no_host_extendX=True,  resizable=True, width=1800) as coil_table_id:
                for i in range(COILSPERROW+1):
                    if i == 0:
                        dpg.add_table_column()
                    else:    
                        dpg.add_table_column(label=i)
                            
            
                for i in range(MAXCOILROWS):
                    with dpg.table_row():
                        for j in range(0,COILSPERROW+1):
                            if j == 0:
                                rowval = COILSPERROW * i
                                dpg.add_text(f"{rowval}")
                            else: 
                                dpg.add_checkbox(tag="coils"+str(i*COILSPERROW+j), callback=coilClicked, user_data=(COILSPERROW*i+j)) 
                                dpg.highlight_table_cell(coil_table_id, i, j, [230, 0, 0, 100])
                                

                
    with dpg.collapsing_header(label="Discrete Output Coil Values CSV Entry"):
        dpg.add_text("Enter comma separated list of coil values as integer values in range 1-9999")
        dpg.add_input_text(default_value="", tag="coilValueInputText", multiline=True)
        dpg.add_button(label="Set Coil Values", callback=setManualCoils, tag="setManualCoilsButton")
        dpg.add_input_text(default_value="Status", tag="coilValueStatusText", readonly=True)


    # 30001 - 39999 - analog input registers - R/O - 16 bit int
    with dpg.collapsing_header(label="Analogue Input Register Values GUI - Doesn't yet update if values are changed by client"):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _register_child_window:

            dpg.add_button(label="Randomise Input Register Values", callback=randomiseRegisters, tag="randomiseRegistersButton")
            dpg.add_button(label="Clear Input Register Values", callback=clearRegisters, tag="clearRegistersButton")
            registerValueGroup = dpg.add_group(horizontal=True)
            dpg.move_item("randomiseRegistersButton", parent=registerValueGroup)
            dpg.move_item("clearRegistersButton", parent=registerValueGroup)

            # grid allowing entry of values 1-MAXREGISTERS
            
            with dpg.table(tag="registersTable", header_row=True, row_background=False,
                                borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit, borders_innerV=True,
                                borders_outerV=True, delay_search=True,no_host_extendX=True,  resizable=True, width=1800) as register_table_id:
                for i in range(REGISTERSPERROW+1):
                    if i == 0:
                        dpg.add_table_column()
                    else:    
                        dpg.add_table_column(label=i)
                            
            
                for i in range(MAXREGISTERROWS):
                    with dpg.table_row():
                        for j in range(0,REGISTERSPERROW+1):
                            if j == 0:
                                rowval = 30000 + (REGISTERSPERROW * i)
                                dpg.add_text(f"{rowval}")
                            else: 
                                dpg.add_input_text(tag="registers"+str(i*REGISTERSPERROW+j),callback=registerTextChanged, decimal=True, width=40, user_data=i*REGISTERSPERROW+j)




    
    # 40001 - 49999 - analog output holding registers - R/W - 16 bit int
    with dpg.collapsing_header(label="Analogue Output Holding Register Values GUI - Doesn't yet update if values are changed by client"):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True) as _output_register_child_window:

            dpg.add_button(label="Randomise Output Register Values", callback=randomiseOutputRegisters, tag="randomiseOutputRegistersButton")
            dpg.add_button(label="Clear Output Register Values", callback=clearOutputRegisters, tag="clearOutputRegistersButton")
            outputRegisterValueGroup = dpg.add_group(horizontal=True)
            dpg.move_item("randomiseOutputRegistersButton", parent=outputRegisterValueGroup)
            dpg.move_item("clearOutputRegistersButton", parent=outputRegisterValueGroup)

            # grid allowing entry of values 1-MAXREGISTERS
            
            with dpg.table(tag="outputRegistersTable", header_row=True, row_background=False,
                                borders_innerH=True, borders_outerH=True, policy=dpg.mvTable_SizingFixedFit, borders_innerV=True,
                                borders_outerV=True, delay_search=True,no_host_extendX=True,  resizable=True, width=1800) as output_register_table_id:
                for i in range(REGISTERSPERROW+1):
                    if i == 0:
                        dpg.add_table_column()
                    else:    
                        dpg.add_table_column(label=i)
                            
            
                for i in range(MAXREGISTERROWS):
                    with dpg.table_row():
                        for j in range(0,REGISTERSPERROW+1):
                            if j == 0:
                                rowval = 40000 + (REGISTERSPERROW * i)
                                dpg.add_text(f"{rowval}")
                            else: 
                                dpg.add_input_text(tag="outputregisters"+str(i*REGISTERSPERROW+j),callback=outputRegisterTextChanged, decimal=True, width=40, user_data=i*REGISTERSPERROW+j)


dpg.create_viewport(title='pyModbusServerGUI')
 
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()

        

