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

def get_attack_distribution(log_file_path):
    """
    
    log_file_path: a string path to the log file you want to read
    
    """
    log_file = []
    with open(log_file_path,"r") as file:
        lines = file.readlines()
        for line in lines:
            log_file.append(line)    
    
    
    pre_neckline_check_raw = []
    [pre_neckline_check_raw.append(line.replace('|',' ').split()[:-1]) for line in log_file if "颈线检测前" in line]
    post_neckline_check_raw = []
    [post_neckline_check_raw.append(line.split()[:-1]) for line in log_file if "出现分时攻击" in line]    
    
    def get_distribution_dict(raw_list):
        distribution_dict = {}
        
        for line in raw_list:
            try:
                time = datetime.datetime.strptime(line[0]+' '+line[1],'%Y-%m-%d %H:%M:%S.%f')
            except:
                time = datetime.datetime.strptime(line[0]+' '+line[1],'%Y-%m-%d %H:%M:%S')
            time = time.strftime('%Y-%m-%d %H:%M')
            attack_ctr = len(line)-2
            try:
                distribution_dict[time]+=attack_ctr
            except:
                distribution_dict[time]=attack_ctr       
                
        return distribution_dict
    
    pre_neckline_dict = get_distribution_dict(pre_neckline_check_raw)
    post_neckline_dict = get_distribution_dict(post_neckline_check_raw)

    pre_neckline_ctrs = -np.array(list(pre_neckline_dict.values()))
    post_neckline_ctrs = list(post_neckline_dict.values())
    
    plt.figure(figsize=(16,10))
    ticks = np.arange(len(pre_neckline_ctrs))
    print(ticks)
    plt.bar(ticks, pre_neckline_ctrs, label = "attacks before neckline check")
    ticks = np.arange(len(post_neckline_ctrs))
    print(ticks)
    plt.bar(ticks, post_neckline_ctrs, label = "attacks after neckline check")
    plt.legend(loc = 'best',fontsize = 15)
    plt.grid()
    plt.show()

if __name__ == "__main__":
    print(get_attack_time_list(600311,"20200204.log"))
    get_attack_distribution("20200204.log")