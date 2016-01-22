# -*- conding:utf-8 -*-
#import
import time
import wx
import os

result = {}
all_dev = set()
start_time = None
end_time = None
time_format = "%Y-%m-%d %H:%M:%S"
def deal_new_line(ln):
    global result, all_dev
    newlst = eval(ln.split(':')[-1])
    #print newlst
    #print set(newlst)
    #print all_dev
    all_dev.update(set(newlst))

def deal_gone_line(ln):
    global result, all_dev
    gone_dev = ln.split(':')[-1].strip()
    if result.has_key(gone_dev):
        result[gone_dev] = result[gone_dev] + 1
    else:
        result[gone_dev] = 1

def deal_line(ln):
    if 'new'in ln:
        deal_new_line(ln)
    elif 'gone' in ln:
        deal_gone_line(ln)

def print_result():
    global result, all_dev
    #print 'result:', result
    print 'all devices:', list(all_dev)
    gone_devs_sorted_list = sorted(result.iteritems(), key = lambda x:x[1], reverse = False)

    offline_times = 0
    for item in gone_devs_sorted_list:
        print item[0], ':', item[1]
        offline_times += item[1]

    print len(result), 'devices have been offlined.'
    last_seconds = time.mktime(end_time) - time.mktime(start_time)
    print 'Total offline times:', offline_times
    print 'Total time:', last_seconds, 'seconds'
    if offline_times == 0:
        print 'No Device offlined.'
    else:
        print 'Device goes offline every', last_seconds / offline_times, 'seconds.'

    gone_devs_set = set(x for x in result)
    unknown_dev = list(gone_devs_set - all_dev)
    if len(unknown_dev):
        print 'unknown device', unknown_dev, 'left'
    left_dev_lst = list(all_dev - gone_devs_set)
    if len(left_dev_lst):
        print left_dev_lst, 'is always online!'


def analyse_main(fn):
    global start_time, end_time
    with open(fn, 'r') as f:
        lines = f.readlines()
        start_time = time.strptime(lines[0][:len("2016-01-19 17:24:54")], time_format)
        end_time = time.strptime(lines[-1][:len("2016-01-19 17:24:54")], time_format)
        for eachLine in lines:
            deal_line(eachLine)
    print_result()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, id = -1, title ="ZigBee Device Test Log Analyse")

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
        self.fin = ''
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
            self.fin = dialog.GetPath()
            self.tc_fin.Clear()
            self.tc_fin.WriteText(self.fin)
        dialog.Destroy()

    def on_clk_analyse(self, event):
        if os.path.isfile(self.fin): #green
            self.tc_out.Clear()
            analyse_main(self.fin)
        else:
            pass #red

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
