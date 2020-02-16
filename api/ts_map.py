"""
@ File:     ts_map.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 00:24
"""
import os
import tushare as ts
# import api.storage as st

CODE_SEGMENT_NUM = 8

code_list = []
detail_code_list = []
ts_mapping = dict()
ts_lower_mapping = dict()

token = os.getenv('TOKEN')
pro = ts.pro_api(token)
if __name__ == '__main__':
    # deprecated
    data = pro.daily(trade_date='20200116').values
    storage = st.Storage()
    storage.update_realtime_storage()
    code_list0 = '{'
    code_list1 = ''
    code_list2 = ''
    code_list3 = '{'
    for code in data:
        # we do not need sci-tech innovation board and special treatment
        if code[0].startswith('688'):
            continue
        try:
            rt = storage.get_realtime_storage_single(code[0][:6])
        except KeyError as e:
            print(code[0] + ' ')
            continue
        if rt[0].startswith('*ST') or rt[0].startswith('ST') or rt[0].startswith('退市'):
            continue
        if code[0].endswith('SH'):
            code_list0 += '\'' + code[0][:6] + '\':\'' + code[0][:6] + '.SH\', '
            code_list1 += '\'sh' + code[0][:6] + '\','
            code_list3 += '\'' + code[0][:6] + '\':\'sh' + code[0][:6] + '\', '
        else:
            code_list0 += '\'' + code[0][:6] + '\':\'' + code[0][:6] + '.SZ\', '
            code_list1 += '\'sz' + code[0][:6] + '\','
            code_list3 += '\'' + code[0][:6] + '\':\'sz' + code[0][:6] + '\', '
    code_list0 = code_list0[:-2] + '}'
    code_list1 = code_list1[:-1]
    code_list3 = code_list3[:-2] + '}'
    i = 0
    code_list2 = ['', '', '', '', '', '', '', '']
    num = int(len(data) / len(code_list2))
    for code in data:
        # we do not need sci-tech innovation board and special treatment
        if code[0].startswith('688'):
            continue
        try:
            rt = storage.get_realtime_storage_single(code[0][:6])
        except KeyError as e:
            print(code[0] + ' ')
            continue
        if rt[0].startswith('*ST') or rt[0].startswith('ST') or rt[0].startswith('退市'):
            continue
        if code[0].endswith('SH'):
            code_list2[int(i / num)] += 'sh' + code[0][:6] + ','
        else:
            code_list2[int(i / num)] += 'sz' + code[0][:6] + ','
        i += 1
    for i in range(0, len(code_list2)):
        code_list2[i] = code_list2[i][:-1]
    breakpoint()
else:
    # construct code-type mapping
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
    detail_code_list = ['sh'+code[:6] if code.endswith('SH') else 'sz'+code[:6] for code, name in
                        zip(data['ts_code'].values, data['name'].values) if not
                        (name.startswith('*ST') or name.startswith('ST') or name.startswith('退市')
                         or code.startswith('688'))]
    ts_mapping = dict([(symbol, code) for symbol, code, name in
                       zip(data['symbol'].values, data['ts_code'].values, data['name'].values) if not
                       (name.startswith('*ST') or name.startswith('ST') or name.startswith('退市') or
                        code.startswith('688'))])
    ts_lower_mapping = dict([(symbol, 'sh'+code[:6]) if code.endswith('SH') else (symbol, 'sz'+code[:6])
                             for symbol, code, name in
                             zip(data['symbol'].values, data['ts_code'].values, data['name'].values) if not
                             (name.startswith('*ST') or name.startswith('ST') or name.startswith('退市') or
                              code.startswith('688'))])
    code_list = [''] * CODE_SEGMENT_NUM
    i = 0
    num = int(len(detail_code_list) / len(code_list))
    for code in detail_code_list:
        index = int(i / num)
        if index >= len(code_list):
            index = len(code_list) - 1
        code_list[index] += code + ','
        i += 1
    for i in range(0, len(code_list)):
        code_list[i] = code_list[i][:-1]
