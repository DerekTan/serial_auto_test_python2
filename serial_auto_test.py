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
        self.group = {1: [0x6ed3, 0x9694],
                      2: [0x8ad6, 0xcf0e, 0x0f01, 0x745f, 
                          0xe5b1, 0x642b, 0xcd88, 0xe37f,
                          0x2b68]}

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
        self.checkbox_autostate = wx.CheckBox(self.cf_panel, -1, 'AutoState')

        #rx
        self.rx_panel = wx.Panel(self, -1)
        self.rx_staticbox = wx.StaticBox(self.rx_panel, -1, "Received Data")
        self.rx_text = wx.TextCtrl(self.rx_panel, pos = (10, 10), style = wx.TE_MULTILINE | wx.TE_READONLY | wx.EXPAND)

        #tx
        self.tx_panel = wx.Panel(self, -1)
        self.tx_staticbox = wx.StaticBox(self.tx_panel, -1, "Transmit Data")

        self.text_tx = []
        self.button_tx = []
        for i in xrange(4):
            self.text_tx.append( wx.TextCtrl(self.tx_panel, -1, style = wx.EXPAND) )
            self.button_tx.append( wx.Button(self.tx_panel, -1, label = "Send", style = wx.ALIGN_RIGHT) )

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
        cf_sizer.Add(self.checkbox_autostate, 0, wx.EXPAND | wx.ALL, 0)
        self.cf_panel.SetSizer(cf_sizer)

        #self.rx_staticbox.Lower()
        rx_sizer = wx.StaticBoxSizer(self.rx_staticbox, wx.VERTICAL)
        rx_sizer.Add(self.rx_text, 1, wx.EXPAND, 0)
        self.rx_panel.SetSizer(rx_sizer)

        # tx
        self.tx_staticbox.Lower()
        sb_tx_sizer = wx.StaticBoxSizer(self.tx_staticbox, wx.VERTICAL)

        tx_sizer = wx.FlexGridSizer(rows = 4, cols = 2, vgap = 5, hgap = 5)

        for i in xrange(4):
            tx_sizer.Add(self.text_tx[i], proportion = 1, flag = wx.EXPAND)
            tx_sizer.Add(self.button_tx[i], proportion = 0)

        tx_sizer.AddGrowableCol(0, proportion = 1) # set column 0 growable, 

        sb_tx_sizer.Add(tx_sizer, 1, wx.EXPAND)
        self.tx_panel.SetSizerAndFit(sb_tx_sizer)

        # right vertical sizer
        rvsizer = wx.BoxSizer(wx.VERTICAL)
        rvsizer.Add(self.rx_panel, 1, wx.EXPAND, 0)
        rvsizer.Add(self.tx_panel, 1, wx.EXPAND, 0)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.cf_panel, 0, wx.EXPAND, 0)
        hsizer.Add(rvsizer, 1, wx.EXPAND, 0)
        #hsizer.Add()
        self.SetSizer(hsizer)
        self.Layout()

    def __attach_events(self):
        #wx.EVT_BUTTON(self, self.button_onoff.GetId(), self.OnOff)
        self.Bind(wx.EVT_BUTTON, self.onclick_OnOff, self.button_onoff)
        self.Bind(wx.EVT_BUTTON, self.onclick_rxclear, self.button_clear_rx)
        self.Bind(wx.EVT_CHECKBOX, self.oncheck_autoroll, self.checkbox_autoroll)
        self.Bind(wx.EVT_CHECKBOX, self.oncheck_autostate, self.checkbox_autostate)

        # bind button_tx[]
        for i in xrange(4):
            self.button_tx[i].Bind( wx.EVT_BUTTON, lambda event, button_num = i : self.onclick_tx(event, button_num) )

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
                #print '[' + instr + ']'
                self.rx_text.AppendText( time.strftime("%H:%M:%S:") +'['+ str(n) + ':')
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
            self.serial.write(str_hex_to_c('FE 00 21 AA'))
            #print str_hex_to_c('FE 00 A0 AA')
            time.sleep(1)
        thread.exit_thread()

    def onclick_tx(self, event, num):
        if self.serial.isOpen():
            if self.text_tx[num].GetNumberOfLines():
                outstr = self.text_tx[num].GetLineText(1)
                self.serial.write(str_hex_to_c(outstr))

    def oncheck_autostate(self, event):
        if self.checkbox_autostate.IsChecked():
            thread.start_new_thread(self.autotest_set_get_dev_state, ())
        else:
            pass

    def autotest_set_get_dev_state(self): #new thread
        with open(time.strftime("%Y-%m-%d_%H-%M-%S") + '-state_test.log', 'a') as f2:
            state = 0
            while self.serial.isOpen() and self.checkbox_autostate.IsChecked():
                for grpid in self.group:
                    self.set_group_state(grpid, state)
                    time.sleep(1)
                    self.check_group_state(grpid, state, f2)
                state = int(not state)
        thread.exit_thread()

    def set_group_state(self, grpid, state):
        if self.serial.isOpen():
            cmd = 'FE 04 82'
            cmd += ' %02x' % state
            cmd += ' %02x' % (grpid & 0xff)
            cmd += ' %02x' % ((grpid >> 8) & 0xff)
            cmd += ' 01 AA'
            print cmd
            self.serial.write(str_hex_to_c(cmd))

    def check_group_state(self, grpid, state, f2):
        for dev in self.group[grpid]:
            self.check_dev_state(dev, state, f2)

    def check_dev_state(self, dev, state, f2):
        self.send_get_dev_state(dev)
        for i in xrange(10):
            time.sleep(0.1)
            ret = self.serial_handler.pop_dev_state(dev)
            print i, str(ret)
            if ret != None:
                if ret != state:
                    f2.write( current_time() + 
                            ' device: %04x state error'%dev + '\n')
                    f2.flush()
                else:
                    pass
                return
        f2.write( current_time() + ' device: %04x state get fail'%dev + '\n')
        f2.flush()
        return
                

    def send_get_dev_state(self, dev):
        if self.serial.isOpen():
            cmd = 'FE 02 87'
            cmd += ' %02x' % (dev & 0xff)
            cmd += ' %02x' % ((dev >> 8) & 0xff)
            cmd += ' AA'
            print cmd
            self.serial.write(str_hex_to_c(cmd))


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()

