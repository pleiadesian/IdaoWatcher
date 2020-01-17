"""
@ File:     neckline.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:20
@ Desc:     Maintaining the state of neckline of stock in time share
"""
import datetime
import api.storage as st


class NeckLine:
    def __init__(self, storage):
        self.neckline = dict()
        self.storage = storage

    def detect_neckline(self, code):
        """
        update the state of neckline
        :param code: stock code
        """
        info = self.storage.get_realtime_storage_single(code)
        price = info[3]
        high = info[4]
        time = info[31]
        if price == high:
            self.neckline[code] = time

    def high_to_curr(self, code):
        curr_time = self.storage.get_realtime_storage_single(code)[31]
        if code not in self.neckline:
            self.neckline[code] = curr_time
        high_time = self.neckline[code].split(':')
        if (9 <= int(high_time[0]) <= 11 and 9 <= int(curr_time[0]) <= 11) or \
                (13 <= (high_time[0]) <= 15 and 13 <= int(curr_time[0]) <= 15):
            return (datetime.datetime.strptime(curr_time[:5], "%H:%M") -
                    datetime.datetime.strptime(high_time[:5], "%H:%M")).seconds / 60
        else:
            return (datetime.datetime.strptime(curr_time[:5], "%H:%M") -
                    datetime.datetime.strptime('13:00', "%H:%M")).seconds / 60 + \
                   (datetime.datetime.strptime('11:30', "%H:%M") -
                    datetime.datetime.strptime(high_time[:5], "%H:%M")).seconds / 60


if __name__ == '__main__':
    storage = st.Storage()
    neckline = NeckLine(storage)
    neckline.detect_neckline('000001')
