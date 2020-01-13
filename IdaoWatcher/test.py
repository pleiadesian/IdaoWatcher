"""
@ File:     test.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 13:50
"""
import tushare as ts
import pyautogui

# ts.set_token('dd8f916cd8c513589798cd4578639a341d6f8eee8fa926e6a9e986b0')
#
# pro = ts.pro_api()

# daily
# df = pro.daily(ts_code='300541.SZ', start_date='20200108', end_date='20200110')

# realtime
# df = ts.get_realtime_quotes('000581')  # Single stock symbol
# a = df

# ts.get_today_all()

# df = ts.get_today_ticks('601333')
# df.head(10)
# a = df


# screenWidth, screenHeight = pyautogui.size()
#
# pyautogui.moveTo(840, 535)
# pyautogui.click(x=None, y=None, clicks=2, interval=1.0, button='left', duration=1.0, tween=pyautogui.linear)
# pyautogui.typewrite(message='000001',interval=0.5)
# pyautogui.press('enter')

# coding:utf-8
import time
import psutil
import win32gui, win32process, win32con, win32com.client
import ctypes


class setf():
    def __init__(self):
        self.gamename = 'TdxW.exe'
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.dll = ctypes.CDLL("user32.dll")

    def setfocus(self):
        pid = self.get_pid_for_pname(self.gamename)
        if pid:
            for hwnd in self.get_hwnds_for_pid(pid):
                self.shell.SendKeys('%')
                self.dll.LockSetForegroundWindow(2)
                if self.dll.IsIconic(hwnd):
                    win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                self.dll.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                self.dll.SetForegroundWindow(hwnd)
                self.dll.SetActiveWindow(hwnd)

    def get_pid_for_pname(self, processName):
        pids = psutil.pids()  # 获取主机所有的PID
        for pid in pids:  # 对所有PID进行循环
            p = psutil.Process(pid)  # 实例化进程对象
            if p.name() == processName:  # 判断实例进程名与输入的进程名是否一致（判断进程是否存活）
                return pid  # 返回
        return 0

    def get_hwnds_for_pid(self, pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
                return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds


if __name__ == '__main__':
    sf = setf()
    while True:
        time.sleep(3)
        try:
            sf.setfocus()
        except Exception as e:
            print(e)