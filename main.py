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

SLEEP_INTERVAL = 3


class Main:
    def __init__(self):
        self.storage = st.Storage()
        self.neckline = nl.NeckLine(self.storage)
        self.time_share_explosion = ex.TimeShareExplosion()

    def matching(self):
        """
        matching in an interval
        :return: matched codes
        """
        matched = []
        for code in tm.ts_mapping:
            # TODO: implement neckline detection
            if self.time_share_explosion.detect_timeshare_explode(self.storage, code, None):
                matched.append(code)
            self.neckline.detect_neckline(code)
        return matched

    def mainloop(self):
        """
        start main loop
        """
        start = 0
        end = 3
        while True:
            if end - start < 3:
                time.sleep(SLEEP_INTERVAL - (end - start))
            self.storage.update_realtime_storage()
            start = time.time()
            codes = self.matching()
            if len(codes) > 0:
                print(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击")
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击"+'\n')
            end = time.time()
            print("main:" + str(end - start))


if __name__ == '__main__':
    main = Main()
    main.mainloop()
