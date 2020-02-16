import time
import psutil
import win32gui, win32process, win32con, win32com.client
import ctypes
import pyautogui

TYPE_INTERVAL = 0.05


class setf():
    def __init__(self):
        self.gamename = 'TdxW.exe'
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.dll = ctypes.CDLL("user32.dll")
        self.pid = self.get_pid_for_pname(self.gamename)

    def setfocus(self):
        while True:
            hwnds = []
            if self.pid:
                for hwnd in self.get_hwnds_for_pid(self.pid):
                    self.shell.SendKeys('%')
                    self.dll.LockSetForegroundWindow(2)
                    if self.dll.IsIconic(hwnd):
                        win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                    self.dll.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                          win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                    self.dll.SetForegroundWindow(hwnd)
                    self.dll.SetActiveWindow(hwnd)
                    hwnds.append(hwnd)
            hwnd_front = self.dll.GetForegroundWindow()
            for hwnd in hwnds:
                if hwnd == hwnd_front:
                    title_text = win32gui.GetWindowText(hwnd)
                    print('-----')
                    print(title_text)
                    print(len(title_text))
                    if len(title_text) > 0:
                        continue
                    if title_text[:2] == '闪电':
                        self.dll.SetForegroundWindow(0)
                        self.dll.SetActiveWindow(0)
                    return

    def get_pid_for_pname(self, processName):
        pids = psutil.pids()  # 获取主机所有的PID
        for pid in pids:  # 对所有PID进行循环
            p = psutil.Process(pid)  # 实例化进程对象
            if p.name() == processName:  # 判断实例进程名与输入的进程名是否一致（判断进程是否存活）
                for hwnd in self.get_hwnds_for_pid(pid):
                    if win32gui.GetWindowText(hwnd)[:2] == '中信':
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


def init_fs():
    screen_width, screen_height = pyautogui.size()
    sf = setf()
    window_info = [sf, screen_width, screen_height]
    return window_info


def open_code(code, window_info, origin_window=None):
    sf = window_info[0]
    sf.setfocus()
    pyautogui.press('backspace')
    pyautogui.typewrite(message=code, interval=0.01)
    pyautogui.press('enter')
    if origin_window is not None:
        origin_window.raise_()
        origin_window.activateWindow()


def sell_code(code, price, amount, window_info):
    sf = window_info[0]
    sf.setfocus()
    pyautogui.press('backspace')
    pyautogui.typewrite(message=code, interval=TYPE_INTERVAL)
    pyautogui.press('enter')
    pyautogui.typewrite(message='.-1', interval=TYPE_INTERVAL)
    pyautogui.press('enter', interval=TYPE_INTERVAL)
    pyautogui.press('up')
    pyautogui.typewrite(message=price, interval=TYPE_INTERVAL)
    pyautogui.press('enter', interval=TYPE_INTERVAL)
    if amount is not None:
        pyautogui.typewrite(message=amount, interval=TYPE_INTERVAL)
    pyautogui.press('enter', interval=TYPE_INTERVAL)
    pyautogui.press('enter', interval=TYPE_INTERVAL)
    pyautogui.press('enter', interval=TYPE_INTERVAL)


if __name__ == '__main__':
    window_info = init_fs()
    open_code("600030", window_info)
