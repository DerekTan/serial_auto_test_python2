import time
import wx

def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class DevFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id = -1, title = "Online Device", size = (700, 500), name = "online_dev")
        self.text_intro = wx.TextCtrl(self, style=wx.TE_LEFT| wx.TE_READONLY)
        self.gs_dev = wx.GridSizer(10,10, 4, 5) #cols, vgap, hgap
        #gs_dev.Add(wx.StaticText(self), wx.EXPAND)

        self.__set_properties()
        self.__do_layout()
        self.__attach_events()

    def __do_layout(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.text_intro, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)
        vbox.Add(self.gs_dev, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)

    def __set_properties(self):
        self.devlst = []
        pass

    def __attach_events(self):
        pass

    def update_online_devlst(self, devlst):
        offlst = self.devlst
        newlst = []
        for dev in devlst:
            #gs_dev.Add(wx.StaticText(self, ), wx.EXPAND)
            self.gs_dev.Add(wx.Button(self, label=str(dev)), wx.EXPAND)
            if dev in self.devlst:
                #update_dev_status(dev, ONLINE)
                offlst.remove(dev)
                pass
            else:
                newlst.append(dev)


class SerialDeal:
    def __init__(self, fn):
        self.data = ''
        self.online = []
        self.logfile = fn
        #self.devframe = DevFrame()
        #self.devframe.Show()

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
        if cmd == chr(0x21):
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
            #self.devframe.update_online_devlst(devlst)

class MyApp(wx.App):
    """Test code"""
    def OnInit(self):
        #wx.InitAllImageHandlers()
        self.frame = DevFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

