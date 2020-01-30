"""
@ File:     main.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:39
"""
import time
import datetime
from random import randint
import core.realtime.neckline as nl
import core.realtime.explode as ex
import core.realtime.open_high as oh
import core.daily.up_num as un
# import api.storage as st
import api.ts_map as tm


TOKEN_PATH = __file__[:-7] + 'api/token/token.txt'

SLEEP_INTERVAL = 3

TEST_HIGHOPEN = 0
TEST_NECKLINE = 1
TIMEING = 0


class Main:
    # def __init__(self):
    #     self.storage = st.Storage()
    #     self.storage.update_realtime_storage()
    #     self.neckline = nl.NeckLine(self.storage)
    #     self.time_share_explosion = ex.TimeShareExplosion()
    #
    # def matching(self):
    #     """
    #     matching in an interval
    #     :return: matched codes
    #     """
    #     if TEST_HIGHOPEN == 1:
    #         matched = []
    #         for code in tm.ts_mapping:
    #             if oh.detect_high_open(self.storage, code):
    #                 matched.append(code)
    #         return matched
    #     else:
    #         matched = []
    #         final_matched = []
    #         boomed = []
    #         for code in tm.ts_mapping:
    #             ret = self.time_share_explosion.detect_timeshare_explode(self.storage, code)
    #             if ret:
    #                 if ret > 1:
    #                     boomed.append(code)
    #                 else:
    #                     matched.append(code)
    #         if len(matched) > 0 or len(boomed) > 0:
    #             print(str(datetime.datetime.now()) + '     ' + ' '.join(matched) + " | " + ' '.join(boomed) + " 颈线检测前")
    #             with open('stock.log', 'a') as f:
    #                 f.write(str(datetime.datetime.now()) + '     ' + ' '.join(matched) + " | " + ' '.join(boomed) + " 颈线检测前"+'\n')
    #             final_matched = self.neckline.detect_neckline(matched, boomed)
    #         if TEST_NECKLINE == 0:
    #             final_matched = matched
    #         return final_matched

    def mock_matching(self):
        """
        :return: 0~10 random stock codes
        """
        codenum = randint(0, 10)
        codes = []
        for i in range(0, codenum):
            code_index = randint(0, len(tm.detail_code_list) - 1)
            codes.append(tm.detail_code_list[code_index][2:])
        return codes

    def mainloop(self):
        """
        start main loop
        """
        start = 0
        end = 3
        while True:
            if end - start < 3:
                time.sleep(SLEEP_INTERVAL - (end - start))
            start = time.time()  # update too fast?
            # self.storage.update_realtime_storage()
            # codes = self.matching()
            # TODO: display codes to UI
            codes = self.mock_matching()
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
