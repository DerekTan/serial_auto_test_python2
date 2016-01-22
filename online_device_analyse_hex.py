# -*- conding:utf-8 -*-
#import
import time
import wx
import os

class DataAnalyse:
    def __init__(self, fn, textctrl):
        self.fin = fn
        self.textctrl = textctrl
        self.dict_gone_dev = {}
        self.all_dev = set()

        self.do_analyse()
        self.show_result()

    def deal_new_line(self, ln):
        newlst = eval(ln.split(':')[-1])
        self.all_dev.update(set(newlst))

    def deal_gone_line(self, ln):
        gone_dev = ln.split(':')[-1].strip()
        if self.dict_gone_dev.has_key(gone_dev):
            self.dict_gone_dev[gone_dev] = self.dict_gone_dev[gone_dev] + 1
        else:
            self.dict_gone_dev[gone_dev] = 1

    def deal_line(self, ln):
        if 'new'in ln:
            self.deal_new_line(ln)
        elif 'gone' in ln:
            self.deal_gone_line(ln)

    def show_result(self):
        self.textctrl.Clear()
        # all devices
        gone_devs_sorted_list = sorted(self.dict_gone_dev.iteritems(), key = lambda x:x[1], reverse = False)

        print 'Total %d devices:'% len(self.all_dev), list(self.all_dev)
        self.textctrl.AppendText('Total %d devices:'% len(self.all_dev) + str(list(self.all_dev)) + '\n')
        print len(self.dict_gone_dev), 'devices have been dropped:'
        self.textctrl.AppendText('%d devices have been dropped.\n'% len(self.dict_gone_dev))

        offline_times = 0
        for item in gone_devs_sorted_list:
            print item[0], ':', item[1]
            self.textctrl.AppendText('\t'+ str(item[0]) + ' : ' + str(item[1]) + '\n')
            offline_times += item[1]

        last_seconds = time.mktime(self.end_time) - time.mktime(self.start_time)
        print 'Total offline times:', offline_times
        self.textctrl.AppendText('Total offline times: %d\n'% offline_times)
        print 'Test time:', last_seconds, 'seconds'
        self.textctrl.AppendText('Test time: %d seconds\n' % last_seconds)
        if offline_times == 0:
            print 'No Device dropped.'
            self.textctrl.AppendText('No Device dropped.\n')
        else:
            print 'Device goes offline every', last_seconds / offline_times, 'seconds.'
            self.textctrl.AppendText('Device goes offline every %f seconds.\n'% (last_seconds / offline_times))

        gone_devs_set = set(x for x in self.dict_gone_dev)
        unknown_dev = list(gone_devs_set - self.all_dev)
        left_dev_lst = list(self.all_dev - gone_devs_set)
        if len(unknown_dev):
            print 'unknown device', unknown_dev, 'left'
            self.textctrl.AppendText('unknown device' + str(unknown_dev) + 'left\n')
        if len(left_dev_lst):
            print left_dev_lst, 'is always online!'
            self.textctrl.AppendText(str(left_dev_lst) + ' is always online!\n')


    def do_analyse(self):
        time_format = "%Y-%m-%d %H:%M:%S"
        with open(self.fin, 'r') as f:
            lines = f.readlines()
            self.start_time = time.strptime(lines[0][:len("2016-01-19 17:24:54")], time_format)
            self.end_time = time.strptime(lines[-1][:len("2016-01-19 17:24:54")], time_format)
            for eachLine in lines:
                self.deal_line(eachLine)

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, id = -1, title ="ZigBee Device Test Log Analyse", size = (700, 500))

        self.panel = wx.Panel(self, -1)
        self.st_fin = wx.StaticText(self.panel, -1, 'Log file:')
        self.tc_fin = wx.TextCtrl(self.panel, -1, style = wx.EXPAND)
        self.bt_fin = wx.Button(self.panel, -1, label = '...', size = (22, 22))

        self.bt_analyse = wx.Button(self.panel, -1, label = 'analyse', style = wx.EXPAND)

        self.tc_out = wx.TextCtrl(self.panel, -1, style = wx.TE_MULTILINE | wx.EXPAND)

        self.__attach_events()
        self.__set_properity()
        self.__do_layout()

    def __set_properity(self):
        self.fin = None
        self.fout = None

    def __do_layout(self):
        # file input
        h_sizer_fin = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer_fin.Add((25, -1))
        h_sizer_fin.Add(self.st_fin, 0, wx.ALIGN_CENTER_VERTICAL, border = 0)
        h_sizer_fin.Add((5, -1))
        h_sizer_fin.Add(self.tc_fin, 1, wx.EXPAND, border = 0)
        h_sizer_fin.Add(self.bt_fin, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, border = 0)
        h_sizer_fin.Add((25, -1))

        # all
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add(h_sizer_fin, 0, wx.EXPAND)
        v_sizer.Add(self.bt_analyse, 0, wx.EXPAND)
        v_sizer.Add(self.tc_out, 1, wx.EXPAND)

        self.panel.SetSizer(v_sizer)
        self.Layout()

    def __attach_events(self):
        self.Bind(wx.EVT_BUTTON, self.on_clk_open_file_dialog, self.bt_fin)
        self.Bind(wx.EVT_BUTTON, self.on_clk_analyse, self.bt_analyse)

    def on_clk_open_file_dialog(self, event):
        wildcard = "log file (*.log)|*.log|" "text file (*.txt)|*.txt|" "All files (*.*)|*.*"
        dialog = wx.FileDialog(parent = None, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = "", wildcard = wildcard, style = wx.OPEN | wx.CHANGE_DIR )
        if dialog.ShowModal() == wx.ID_OK:
            self.tc_fin.Clear()
            self.tc_fin.WriteText(dialog.GetPath())
        dialog.Destroy()

    def on_clk_analyse(self, event):
        self.fin = self.tc_fin.GetLineText(1)
        if os.path.isfile(self.fin): #green
            self.tc_out.Clear()
            self.analyse = DataAnalyse(self.fin, self.tc_out)
        else:
            pass #red

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show(True)
        frame.Center(wx.BOTH)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
