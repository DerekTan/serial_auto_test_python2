import time
import serial_deal
import wx

def str_hex_to_c(s):
    return ''.join(str(chr(int('0x'+ x, 16))) for x in s.split())

def str_c_to_hex(s):
    return ''.join('%02x '%ord(c) for c in s)

def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class MyApp(wx.App):
    """Test code"""
    def OnInit(self):
        #wx.InitAllImageHandlers()
        #self.frame = DevFrame()
        #self.frame.Show(True)
        #self.SetTopWindow(self.frame)
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

fn = time.strftime("%Y-%m-%d_%H_%M_%S") + '.log'
try:
    logfile = open( fn, 'a')
except IOError as err:
    logfile = None
    print str(err)

app = wx.PySimpleApp()
app.MainLoop()

if logfile:
    serial_handler = serial_deal.SerialDeal(logfile)

    serial_handler.pre_deal(str_hex_to_c('FE 18 A0 CD E6 65 F4 25 3B CF 35 4E 74 FE 8A 73 AF 81 21 61 57 F1 9E 24 98 84 81 AA'))
    serial_handler.pre_deal(str_hex_to_c('FE 16 A0 CD E6 65 F4 25 3B CF 35 4E 74 FE 8A 73 AF 81 21 61 57 F1 9E 24 99 AA'))
    serial_handler.pre_deal(str_hex_to_c('FE 18 A0 CD E6 65 F4 25 3B CF 35 4E 74 FE 8A 73 AF 81 21 61 57 F1 9E 24 99 01 00 AA'))
    serial_handler.pre_deal(str_hex_to_c('FE 18 A0 CD E6 65 F4 25 3B CF 35 4E 74 FE 8A 73 AF 81 21 61 57 F1 9E 24 99 01 00 AA'))
    logfile.close()
