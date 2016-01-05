import wx
import serial
import serial.tools.list_ports
import thread
import time
import serial_deal

def str_hex_to_c(s):
    return ''.join(str(chr(int('0x'+ x, 16))) for x in s.split())

def str_c_to_hex(s):
    return ''.join('%02x '%ord(c) for c in s)

def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class MyFrame(wx.Frame):
    def __init__(self):
        self.serial = serial.Serial()

        wx.Frame.__init__(self, None, id = -1, title = "UART TEST", size = (700, 500), name = "main")

        #configuration
        self.cf_panel = wx.Panel(self, -1)
        self.cf_staticbox = wx.StaticBox(self.cf_panel, -1, "Configurations")
        self.port_label = wx.StaticText(self.cf_panel, -1, "Port")
        self.port_choice = wx.Choice(self.cf_panel, -1, choices = [])
        self.baudrate_label = wx.StaticText(self.cf_panel, -1, "Baudrate")
        self.baudrate_combo = wx.ComboBox(self.cf_panel, -1, choices = [], style = wx.CB_DROPDOWN)
        self.button_onoff = wx.Button(self.cf_panel, -1, label='')
        self.button_clear_rx = wx.Button(self.cf_panel, -1, label='ClearRx')
        #self.button_autoroll = wx.Button(self.cf_panel, -1, label='AutoRoll')
        self.checkbox_autoroll = wx.CheckBox(self.cf_panel, -1, 'AutoRoll')

        #rx
        self.rx_panel = wx.Panel(self, -1)
        self.rx_staticbox = wx.StaticBox(self.rx_panel, -1, "Received Data")
        self.rx_text = wx.TextCtrl(self.rx_panel, pos = (10, 10), size = (700, 200), style = wx.TE_MULTILINE | wx.TE_READONLY | wx.EXPAND)

        #tx
        self.tx_panel = wx.Panel(self, -1)
        self.tx_staticbox = wx.StaticBox(self.tx_panel, -1, "Transmit Data")
        self.tx_text = wx.TextCtrl(self.tx_panel, pos = (10, 210), size = (700, 200), style = wx.TE_MULTILINE | wx.EXPAND)
        self.button_send = wx.Button(self.tx_panel, -1, label='Send')

        self.__set_properties()
        self.__do_layout()
        self.__attach_events()

    def __set_properties(self):
        # fill in ports and select current setting
        preferred_index = 0
        self.port_choice.Clear()
        self.ports = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            #self.port_choice.Append('%s - %s' % (portname, desc))
            self.port_choice.Append("%s"%portname)
            self.ports.append(portname)
            if self.serial.name == portname:
                preferred_index = n
        self.port_choice.SetSelection(preferred_index)

        preferred_index = None
        # fill in baud rates and select current setting
        self.baudrate_combo.Clear()
        for n, baudrate in enumerate(self.serial.BAUDRATES):
            self.baudrate_combo.Append(str(baudrate))
            if self.serial.baudrate == baudrate:
                preferred_index = n
        if preferred_index is not None:
            self.baudrate_combo.SetSelection(preferred_index)
        else:
            self.baudrate_combo.SetValue(u'%d' % (self.serial.baudrate,))

        if self.serial.isOpen() == True:
            self.button_onoff.SetLabel('Close')
        else:
            self.button_onoff.SetLabel('Open')

    def __do_layout(self):
        #self.cf_staticbox.Lower()
        cf_sizer = wx.StaticBoxSizer(self.cf_staticbox, wx.VERTICAL)
        #cf_sizer.Add(self.cf_staticbox, 0, wx.EXPAND, 0)
        cf_sizer.Add(self.port_label, 0, wx.EXPAND, 0)
        cf_sizer.Add(self.port_choice, 0, wx.EXPAND, 0)
        cf_sizer.Add(self.baudrate_label, 0, wx.EXPAND, 0)
        cf_sizer.Add(self.baudrate_combo, 0, wx.EXPAND, 0)
        cf_sizer.Add(self.button_onoff, 0, wx.EXPAND | wx.ALL, 0)
        cf_sizer.Add(self.button_clear_rx, 0, wx.EXPAND | wx.ALL, 0)
        #cf_sizer.Add(self.button_autoroll, 0, wx.EXPAND | wx.ALL, 0)
        cf_sizer.Add(self.checkbox_autoroll, 0, wx.EXPAND | wx.ALL, 0)
        self.cf_panel.SetSizer(cf_sizer)

        self.rx_staticbox.Lower()
        rx_sizer = wx.StaticBoxSizer(self.rx_staticbox, wx.VERTICAL)
        rx_sizer.Add(self.rx_text, 1, wx.EXPAND, 0)
        self.rx_panel.SetSizer(rx_sizer)

        self.tx_staticbox.Lower()
        tx_sizer = wx.StaticBoxSizer(self.tx_staticbox, wx.VERTICAL)
        tx_sizer.Add(self.tx_text, 1, wx.EXPAND, 0)
        tx_sizer.Add(self.button_send, 0, wx.ALIGN_RIGHT, 0)
        self.tx_panel.SetSizer(tx_sizer)

        rvsizer = wx.BoxSizer(wx.VERTICAL)
        rvsizer.Add(self.rx_panel, 1, wx.EXPAND, 0)
        rvsizer.Add(self.tx_panel, 1, wx.EXPAND, 0)
        #self.rx_panel.SetSizer(rvsizer)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.cf_panel, 0, wx.EXPAND, 0)
        hsizer.Add(rvsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 0)
        #hsizer.Add()
        self.SetSizer(hsizer)
        self.Layout()

    def __attach_events(self):
        #wx.EVT_BUTTON(self, self.button_onoff.GetId(), self.OnOff)
        self.Bind(wx.EVT_BUTTON, self.onclick_OnOff, self.button_onoff)
        self.Bind(wx.EVT_BUTTON, self.onclick_rxclear, self.button_clear_rx)
        self.Bind(wx.EVT_CHECKBOX, self.oncheck_autoroll, self.checkbox_autoroll)
        self.Bind(wx.EVT_BUTTON, self.oncheck_send, self.button_send)

    def onclick_OnOff(self, event):
        if self.button_onoff.GetLabel() == 'Open':
            self.serial_open()
        else:
            self.serial_close()
        #set button label
        if self.serial.isOpen() == True:
            thread.start_new_thread(self.serial_receive,())
            self.button_onoff.SetLabel('Close')
        else:
            self.button_onoff.SetLabel('Open')


    def serial_open(self):
        success = True

        #port
        self.serial.port = self.ports[self.port_choice.GetSelection()]
        print self.serial

        #baudrate
        try:
            b = int(self.baudrate_combo.GetValue())
        except ValueError:
            with wx.MessageDialog(
                    self,
                    'Baudrate must be a numeric value',
                    'Value Error',
                    wx.OK | wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            success = False
        else:
            self.serial.baudrate = b
        print self.serial.baudrate

        if success == True:
            try:
                self.serial.open()
            except:
                print 'serial port open error'

    def serial_close(self):
        self.serial.close()

    def serial_receive(self):
        fn = time.strftime("%Y-%m-%d_%H-%M-%S") + '.log'
        try:
            logfile = open( fn, 'a')
        except IOError as err:
            logfile = None
            print str(err)

        if logfile:
            self.serial_handler = serial_deal.SerialDeal(logfile)

        while self.serial.isOpen():
            n = self.serial.inWaiting()
            if n != 0:
                instr = self.serial.read(n)
                if logfile:
                    self.serial_handler.pre_deal(instr)
                print '[' + instr + ']'
                self.rx_text.AppendText( time.strftime("%Y-%m-%d %H:%M:%S:") +'['+ str(n) + ':')
                try:
                    self.rx_text.AppendText(instr)
                except UnicodeDecodeError as err:
                    print str(err)
                self.rx_text.AppendText(']')
                self.rx_text.AppendText(str_c_to_hex(instr))
                self.rx_text.AppendText('\n')
            time.sleep(0.1)
        if logfile:
            logfile.close()
        thread.exit_thread()

    def onclick_rxclear(self, event):  # wxGlade: TerminalFrame.<event_handler>
        """Clear contents of output window."""
        self.rx_text.Clear()

    def oncheck_autoroll(self, event):
        if self.checkbox_autoroll.IsChecked():
            thread.start_new_thread(self.serial_autoroll,())
        else:
            pass

    def serial_autoroll(self):
        while self.serial.isOpen() and self.checkbox_autoroll.IsChecked():
            self.serial.write(str_hex_to_c('FE 00 A0 AA'))
            print str_hex_to_c('FE 00 A0 AA')
            time.sleep(1)
        thread.exit_thread()

    def oncheck_send(self, event):
        if self.serial.isOpen():
            print self.tx_text.GetNumberOfLines()
            for n in range(0, self.tx_text.GetNumberOfLines()):
                #print n,
                outstr = self.tx_text.GetLineText(n)
                #print outstr
                self.serial.write(str_hex_to_c(outstr))

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
