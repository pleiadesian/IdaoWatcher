"""
@ File:     test.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 13:50
"""
import tushare as ts
import pyautogui
import setfocus

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


screen_width, screen_height = pyautogui.size()

sf = setfocus.setf()
sf.setfocus()

pyautogui.moveTo(screen_width / 2, screen_height / 2)
pyautogui.click(x=None, y=None, clicks=1, interval=0.0, button='left', duration=0.0, tween=pyautogui.linear)
pyautogui.typewrite(message='000001', interval=0.01)
pyautogui.press('enter')
