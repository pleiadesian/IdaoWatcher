"""
@ File:     eval_freq.py
@ Author:   pleiadesian
@ Datetime: 2020-02-05 17:23
"""

import datetime
import numpy as np
import matplotlib.pyplot as plt

def get_attack_time_list(stock_id,log_file_path):
    """
    stock_id: an int indicating the id of a stock
    log_file_path: a string path to the log file you want to read
    """
    
    log_file = []
    with open(log_file_path,"r") as file:
        lines = file.readlines()
        for line in lines:
            log_file.append(line)
            
    time_share_attack_raw = []
    [time_share_attack_raw.append(line.split()[:-1]) for line in log_file if "出现分时攻击" in line]
    
    return_list = []
    for line in time_share_attack_raw:
        if str(stock_id) in line:
            return_list.append(line[0]+' '+line[1])
            
    return return_list

"""
# log file pre-process
time_share_attack_raw = []
[time_share_attack_raw.append(line.split()[:-1]) for line in log_file if "出现分时攻击" in line]

# create dictionary
time_share_attack_dict = {}
for line in log_file:
    time = datetime.datetime.strptime(line[0]+' '+line[1],'%Y-%m-%d %H:%M:%S.%f')
    time = time.strftime('%Y-%m-%d %H:%M')
    attack_ctr = len(line)-2
    try:
        time_share_attack_dict[time]+=attack_ctr
    except:
        time_share_attack_dict[time]=attack_ctr

times = list(time_share_attack_dict.keys())
attack_ctrs = list(time_share_attack_dict.values())
ticks = np.arange(len(attack_ctrs))
plt.figure(figsize=(18,10))
plt.bar(ticks, attack_ctrs)
#plt.xticks(ticks, times)
plt.show()
"""

if __name__ == "__main__":
    print(get_attack_time_list(600311,"20200204.log"))