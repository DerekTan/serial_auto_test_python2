#import
import time
import wx

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
    print 'Device goes offline every', last_seconds / offline_times, 'seconds.'

    gone_devs_set = set(x for x in result)
    unknown_dev = list(gone_devs_set - all_dev)
    if len(unknown_dev):
        print 'unknown device', unknown_dev, 'left'
    left_dev_lst = list(all_dev - gone_devs_set)
    if len(left_dev_lst):
        print left_dev_lst, 'is always online!'


def main():
    global start_time, end_time
    fn = raw_input("input file name:")
    with open(fn, 'r') as f:
        lines = f.readlines()
        start_time = time.strptime(lines[0][:len("2016-01-19 17:24:54")], time_format)
        end_time = time.strptime(lines[-1][:len("2016-01-19 17:24:54")], time_format)
        for eachLine in lines:
            deal_line(eachLine)
    print_result()

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, ID = -1, title = "ZigBee Device Test Log Analyse")

        self.panel = wx.Panel(self, -1)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
