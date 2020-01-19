## 分时缘起的通达信内置函数实现

##### 分时

以下所有周期为分时级别，统计范围为当天分时。

##### 分时爆点（使用中）
```
INPUT:开幅上限(3,-9,9),开幅下限(-2,-9,9),冲高至多(5,-9,9),下砸底限(-3,-9,9),间隔分钟至少(30,2,230),单分万元上(100,1,9000)
收价:CLOSE,COLORWHITE,LINETHICK2,PRECIS2;  # 赋予变量的同时，在图上画出线
开幅:=(DYNAINFO(4)-DYNAINFO(3))/DYNAINFO(3)*100;  # 今开相对于昨收，注意百分比的百分号是不计入的
涨跌:=(CLOSE-DYNAINFO(3))/DYNAINFO(3)*100;  # 当前价相对于昨收，CLOSE会动态变化
开冲砸:开幅<=开幅上限 AND 开幅>=开幅下限 AND REF(HHV(涨跌,0)<=冲高至多 AND LLV(涨跌,0)>=下砸底限,1),LINETHICK0,PRECIS0;  # HHV统计的是在当天分时范围里的
高距今:REF(HHVBARS(CLOSE,0),1)+1,LINETHICK0,PRECIS0;  # 最高点到现在的天数
前高价:REF(CLOSE,高距今),LINETHICK0,PRECIS2;  # 取出最高点的价格
# 突破的核心逻辑：
# * 一分钟的成交额超过了100万元
# * 当天涨幅超过1.58%
# * 当前价格已经突破今天分时高头
# * 前高头离现在必须要大于30分钟
# * 现量和流通盘的比值必须大于60%
# * 放量超过5分钟均量*常数（常数=240/开盘到现在分钟数，这考虑到时间后推，放量的阈值就要越小）
# * 当天开盘必须在（-2%,3%）的范围里，最高价必须低于%5，最低价必须高于-3%（开冲砸的定义）
# 注意：C是CLOSE的简写
突破:AMOUNT/10000>=单分万元上 AND 涨跌>=1.58 AND CLOSE>前高价*1.000 AND 高距今>=间隔分钟至少 AND SUM(VOL,0)/CAPITAL*100>=0.6 AND (SUM(VOL,0)*240/DYNAINFO(38)/BARSCOUNT(c))>=0.6 AND 开冲砸,LINETHICK0,PRECIS0;
# 标出突破股票
有过突:COUNT(突破,0),LINETHICK0,PRECIS0;
DRAWTEXT(突破,CLOSE*1.008,'突'),COLORYELLOW,LINETHICK2;
{9:30-10：00 成交量是昨天的4分之一以上 
10：00- 11：30 成交量是昨天的 3分之一 以上 
1:00-3：00 成交量是昨天的3分之2以上};
```

突破的核心逻辑：
* 一分钟的成交额超过了100万元
* 当天涨幅超过1.58%
* 当前价格已经突破今天分时高头
* 前高头离现在必须要大于30分钟
* 换手率>6%
* 量比>0.6
* 当天开盘必须在（-2%,3%）的范围里，最高价必须低于%5，最低价必须高于-3%（开冲砸的定义）

#####  高开上穿均线

```
INPUT:时分之前(1055,933,1455),开幅大于(0.5,-11,11),开幅小于(6.0,-11,11),量比大于(2.5,0.1,90),换率大于(3,-11,11),涨幅至少(2.5,-11,11),流值小于(80,1,900);
M:=BARSLAST(HOUR=9 AND MINUTE=31)+1;  # 开盘以来经过的分钟数
XX:=SUM(AMOUNT,BARSCOUNT(C))/SUM(VOL*100,BARSCOUNT(C));   # 均价线在当时的值（成交金额/成交股数）
BB:=BETWEEN(C/XX,C+H,C-H);
平衡线:=IF(BB=0,MA(C,BARSCOUNT(C)),XX);
开幅:=(DYNAINFO(4)-DYNAINFO(3))/DYNAINFO(3)*100;
涨幅:=(CLOSE-DYNAINFO(3))/DYNAINFO(3)*100;
高幅:=(HHV(CLOSE,M)-DYNAINFO(3))/DYNAINFO(3)*100;
低幅:=(LLV(CLOSE,M)-DYNAINFO(3))/DYNAINFO(3)*100;
量比线:=sum(vol,0)*240/dynainfo(38)/barscount(c);
换率:=sum(vol,M)/CAPITAL*100;
BBDD:=CROSS(CLOSE,平衡线) AND M>=2 AND 量比线>=量比大于 AND 换率>=换率大于 AND 涨幅>=涨幅至少;
TTKA:=BBDD AND COUNT(BBDD,M)<=6 AND 开幅>=开幅大于 AND 开幅<=开幅小于 AND TIME/100<=时分之前  AND CAPITAL/1000000*CLOSE<=流值小于;
有过:COUNT(TTKA,M)>=1;
;
```

看上去依赖于很多金融指标，按理说判断当前价上传均价线即可。



### DEPRICATED

---

##### 跳空缺口

```
{向下跳空缺口}
I1:=0;
flag1:=0;
while I1<BARSLAST(DISPSTATUS=1)-BARSLAST(DISPSTATUS=2)
DO  
        IF REF(H,I1)<REF(L,I1+1) AND REF(L,I1+1)>HHV(H,I1+1)
           THEN   BEGIN     FLAG1:=1;
                            S1:=I1;
                            I1:=BARSLAST(DISPSTATUS=1);                        
                  END
        ELSE  I1:=I1+1;            
   STICKLINE(FLAG1,REF(L,S1+1),HHV(H,S1+1),(s1+1)*20,0),ColorC0C0C0,ALIGN1,LAYER7;
  DRAWTEXT(flag1,REF(L,s1+1),NUMTOSTRN(ref(l,s1+1),2)+'-'+NUMTOSTRN(hhV(h,S1+1),2)),ALIGN2,COLORgreen;

{向上跳空缺口}
I:=0;
flag:=0;
while I<BARSLAST(DISPSTATUS=1)-BARSLAST(DISPSTATUS=2)
DO  
        IF REF(L,I)>REF(H,I+1) AND REF(H,I+1)<LLV(LOW,I+1)
           THEN   BEGIN     FLAG:=1;
                            S:=I;
                            I:=BARSLAST(DISPSTATUS=1);                        
                  END
        ELSE  I:=I+1;            
   STICKLINE(FLAG,REF(h,S+1),LLV(LOW,S+1),20*(s+1),500),ColorC0C0C0,ALIGN1,LAYER7;
 DRAWTEXT(FLAG,REF(H,s+1),NUMTOSTRN(ref(h,s+1),2)+'-'+NUMTOSTRN(LLV(LOW,S+1),2)),ALIGN2,COLORred;
```

##### 分时爆点（已废弃）

```
INPUT:开幅上限(3,-9,9),开幅下限(-2,-9,9),冲高至多(5,-9,9),下砸底限(-3,-9,9),间隔分钟至少(30,2,230),单分手数少(1000,500,9000);  # 1分钟手数至少？
收价:CLOSE,COLORWHITE,LINETHICK2,PRECIS2;  # 赋予变量的同时，在图上画出线
五均:(CLOSE+"分爆引用.昨日四价和#DAY")/5,COLORWHITE,DOTLINE;  # close是动态更新的，是否会遇到5均线止损一样的问题
十均:(CLOSE+"分爆引用.昨日九价和#DAY")/10,COLORFF00FF,DOTLINE;
踏上双线:=CLOSE>五均 AND CLOSE>十均;
开幅:=(DYNAINFO(4)-DYNAINFO(3))/DYNAINFO(3)*100;  # 今开相对于昨收，注意百分比的百分号是不计入的
涨跌:=(CLOSE-DYNAINFO(3))/DYNAINFO(3)*100;  # 当前价相对于昨收，CLOSE会动态变化
开冲砸:开幅<=开幅上限 AND 开幅>=开幅下限 AND REF(HHV(涨跌,0)<=冲高至多 AND LLV(涨跌,0)>=下砸底限,1),LINETHICK0,PRECIS0;  # HHV统计的是什么范围里的
高距今:REF(HHVBARS(CLOSE,0),1)+1,LINETHICK0,PRECIS0;  # 最高点到现在的天数
前高价:REF(CLOSE,高距今),LINETHICK0,PRECIS2;  # 取出最高点的价格
TTT:=SUM(VOL,0)/"分爆引用.昨日四价和#DAY";  # 为什么用成交量除以均价，是否为了估算量比？单位为vol/price是否合理？（考虑高价小盘股和低价大盘股）
# 注意TIME是时分秒，例如093135
# 对量比的要求：
# * 在前半个小时，要检查TTT是否大于25%
# * 在10点后到11点半前，要检查TTT是否大于33%
# * 在下午，要检查TTT是否大于67%
量返回:IF(TIME/100>=931 AND TIME/100<=1000,TTT>=0.25,IF(TIME/100>1000 AND TIME/100<=1129,TTT>=0.33,IF(TIME/100>=1301 AND TIME/100<=1457,TTT>=0.67,0))),LINETHICK0,PRECIS0;
# 突破的核心逻辑：
# * 量比达到要求（TTT是当前成交量除以近5分钟均价，为什么第一个条件不是“量返回”）
#       * 在前半个小时，要检查TTT是否大于25%
#       * 在10点后到11点半前，要检查TTT是否大于33%
#       * 在下午，要检查TTT是否大于67%
# * 一分钟的量超过阈值（分时的VOL是一分钟的VOL，还是3秒更新的VOL？）
# * 当天涨幅超过1%
# * 当前价格已经突破今天分高头的0.1%
# * 前高头离现在必须要大于30分钟
# * 当天开盘必须在（-2%,3%）的范围里，最高价必须低于%5，最低价必须高于-3%
# BUG: 此处TTT应该改为量返回
突破:TTT AND 踏上双线 AND VOL>=单分手数少 AND 涨跌>=1 AND CLOSE>前高价*1.001 AND 高距今>=间隔分钟至少 AND 开冲砸,LINETHICK0,PRECIS0;
# 标出突破股票
有过突:COUNT(突破,0),LINETHICK0,PRECIS0;
DRAWTEXT(突破,CLOSE*1.008,'突'),COLORYELLOW,LINETHICK2;
{9:30-10：00 成交量是昨天的4分之一以上 
10：00- 11：30 成交量是昨天的 3分之一 以上 
1:00-3：00 成交量是昨天的3分之2以上};
```

##### 