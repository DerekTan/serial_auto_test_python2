import time
import wx

def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class DevFrame(wx.Frame):
    def __do_layout(self):
        pass

    def __set_properties(self):
        pass

    def __attach_events(self):
        pass

class SerialDeal:
    def __init__(self, fn):
        self.data = ''
        self.online = []
        self.logfile = fn

    def pre_deal(self, instr):
        self.data += instr
        start_idx = -1
        start_idx = self.data.find(chr(0xfe))
        while -1 != start_idx:
            data_len = ord(self.data[start_idx + 1])
            cmd = self.data[start_idx + 2]
            data_idx = start_idx + 3
            if self.data[data_idx + data_len] == chr(0xaa):
                self.deal(cmd, self.data[data_idx : data_idx+data_len])
                self.data = self.data[data_idx+data_len+1:]
            else:
                self.data = self.data[start_idx+1:]
            start_idx = self.data.find(chr(0xfe))

    def deal(self, cmd, data):
        devlst = []
        newlst = []
        #print 'online:', self.online
        if cmd == chr(0xa0):
            n = 0
            for c in data:
                if n == 0:
                    tmpdev = ord(c)
                else:
                    tmpdev += ord(c) << 8
                    devlst.append(tmpdev)
                    #print type(tmpdev)
                    if tmpdev in self.online:
                        #print tmpdev, 'in online'
                        pass
                    else:
                        #print tmpdev, 'not in online'
                        newlst.append(tmpdev)
                n = (n+1) % 2

            for tmpdev in self.online:
                if tmpdev not in devlst:
                    self.logfile.write(current_time() + ':'
                            + 'device gone: ' + str(tmpdev) + '\n')
                    self.logfile.flush()

                    print 'device gone:', str(tmpdev)
            if len(newlst):
                self.logfile.write(current_time() + ':'
                        + 'new device: ' + str(newlst) + '\n')
                self.logfile.flush()
                print 'newlst:',newlst
            self.online = devlst[:]

class MyApp(wx.App):
    """Test code"""
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.frame = SerialDeal()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return 0

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

