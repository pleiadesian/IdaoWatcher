"""
@ File:     main.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:39
"""
import time
import datetime
import core.realtime.neckline as nl
import core.realtime.explode as ex
import core.realtime.open_high as oh
import core.daily.up_num as un
import api.storage as st
import api.ts_map as tm

SLEEP_INTERVAL = 3

TEST_NECKLINE = 1
TIMEING = 0


class Main:
    def __init__(self):
        self.storage = st.Storage()
        self.storage.update_realtime_storage()
        self.neckline = nl.NeckLine(self.storage)
        self.time_share_explosion = ex.TimeShareExplosion()

    def matching(self):
        """
        matching in an interval
        :return: matched codes
        """
        if datetime.datetime.now() < datetime.datetime.strptime('09:30:00', '%H:%M:%S'):
            matched = []
            for code in tm.ts_mapping:
                if oh.detect_high_open(self.storage, code):
                    matched.append(code)
            return matched
        else:
            matched = []
            boomed = []
            final_matched = []
            for code in tm.ts_mapping:
                ret = self.time_share_explosion.detect_timeshare_explode(self.storage, code)
                if ret:
                    if ret > 1:
                        boomed.append(code)
                    else:
                        matched.append(code)
            if len(matched) > 0 or len(boomed) > 0:
                print(str(datetime.datetime.now()) + '     ' + ' '.join(matched) + " | " + ' '.join(boomed) + " 颈线检测前")
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + '     ' + ' '.join(matched) + " | " + ' '.join(boomed) +
                            " 颈线检测前"+'\n')
                final_matched = self.neckline.detect_neckline(matched, boomed)
            if TEST_NECKLINE == 0:
                final_matched = matched + boomed
            return final_matched

    def mainloop(self):
        """
        start main loop
        """
        start = 0
        end = 3
        while True:
            if end - start < 3:
                time.sleep(SLEEP_INTERVAL - (end - start))
            if end - start > 5:
                print(str(datetime.datetime.now()) + ' BLOCKED FOR ' + str(end - start) + ' s')
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + ' BLOCKED FOR ' + str(end - start) + ' s' + '\n')
            self.storage.update_realtime_storage()
            start = time.time()  # update too fast?
            codes = self.matching()
            if len(codes) > 0:
                print(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击")
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + '     ' + ' '.join(codes) + " 出现分时攻击"+'\n')
            else:
                print(str(datetime.datetime.now()))
                with open('stock.log', 'a') as f:
                    f.write(str(datetime.datetime.now()) + '\n')
            end = time.time()
            # print("main:" + str(end - start))


if __name__ == '__main__':
    main = Main()
    main.mainloop()
