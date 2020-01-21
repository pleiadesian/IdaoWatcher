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

SLEEP_INTERVAL = 1

DEBUG = 1


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
            # TODO: implement neckline detection
            if ex.detect_timeshare_explode(self.storage, code, None):
                matched.append(code)
            self.neckline.detect_neckline(code)
        return matched

    def mainloop(self):
        """
        start main loop
        """
        while True:
            time.sleep(SLEEP_INTERVAL)
            if DEBUG == 1:
                start = time.time()
            self.storage.update_realtime_storage()
            codes = self.matching()
            if len(codes) > 0:
                print(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击")
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击"+'\n')
            if DEBUG == 1:
                end = time.time()
                print("main:" + str(end - start))


if __name__ == '__main__':
    main = Main()
    main.mainloop()
