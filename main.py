"""
@ File:     main.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:39
"""
import time
import datetime
import core.realtime.neckline as nl
import core.realtime.explode as ex
import api.storage as st
import api.ts_map as tm

SLEEP_INTERVAL = 2


class Main:
    def __init__(self):
        self.storage = st.Storage()
        self.neckline = nl.NeckLine(self.storage)

    def matching(self):
        """
        matching in an interval
        :return: matched codes
        """
        matched = []
        for code in tm.ts_mapping:
            if ex.detect_timeshare_explode(code, self.neckline.high_to_curr(code)):
                matched.append(code)
            self.neckline.detect_neckline(code)
        return matched

    def mainloop(self):
        """
        start main loop
        """
        while True:
            time.sleep(SLEEP_INTERVAL)
            self.storage.update_realtime_storage()
            codes = self.matching()
            print(str(datetime.datetime.now()) + '\t' + ' '.join(codes) + " 出现分时攻击")


if __name__ == '__main__':
    main = Main()
    main.mainloop()
