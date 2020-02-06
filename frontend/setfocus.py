import time
import psutil
import win32gui, win32process, win32con, win32com.client
import ctypes
import pyautogui


class setf():
    def __init__(self):
        self.gamename = 'TdxW.exe'
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.dll = ctypes.CDLL("user32.dll")
        self.pid = self.get_pid_for_pname(self.gamename)

    def setfocus(self):
        if self.pid:
            # TODO: detect focus until success
            for hwnd in self.get_hwnds_for_pid(self.pid):
                self.shell.SendKeys('%')
                self.dll.LockSetForegroundWindow(2)
                if self.dll.IsIconic(hwnd):
                    win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                self.dll.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                self.dll.SetForegroundWindow(hwnd)
                self.dll.SetActiveWindow(hwnd)
            for hwnd in self.get_hwnds_for_pid(self.pid):
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
                for hwnd in self.get_hwnds_for_pid(pid):
                    a = win32gui.GetWindowText(hwnd)
                    # TODO: HIGH RISK! DO NOT input code to '闪电买入' and '闪电卖出'
                    if win32gui.GetWindowText(hwnd)[:2] == '中信':
                        return pid  # 返回
                        # print(win32gui.GetWindowText(hwnd))
                    # print(win32gui.GetWindowText(hwnd))
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


def init_fs():
    screen_width, screen_height = pyautogui.size()
    sf = setf()
    window_info = [sf, screen_width, screen_height]
    return window_info


def open_code(code, window_info, origin_window=None):
    sf = window_info[0]
    screen_width = window_info[1]
    screen_height = window_info[2]
    sf.setfocus()
    # pyautogui.moveTo(screen_width / 2, screen_height / 2)
    # pyautogui.click(x=None, y=None, clicks=1, interval=0.0, button='left', duration=0.0, tween=pyautogui.linear)
    code = '0'+code  # why huawei matebook need padding?
    print(code)
    # pyautogui.press('enter', interval=0.01)
    pyautogui.typewrite(message=code, interval=0.01)
    pyautogui.press('enter')
    # pyautogui.typewrite(message=code, interval=0.01)
    if origin_window is not None:
        origin_window.raise_()
        origin_window.activateWindow()


if __name__ == '__main__':
    window_info = init_fs()
    open_code("600030", window_info)
