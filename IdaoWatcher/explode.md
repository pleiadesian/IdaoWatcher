## 分时缘起的通达信内置函数实现


##### 变量定义
```
昨日量能:REF(VOL,1);  # 昨日成交量
昨日四价和:REF(SUM(CLOSE,4),1);  # 昨日开始往前4天的收盘价之和
昨日九价和:REF(SUM(CLOSE,9),1);
```

##### 分爆预警（已废弃）
```
INPUT:开幅上限(3,-9,9),开幅下限(-2,-9,9),冲高至多(5,-9,9),下砸底限(-3,-9,9),间隔分钟至少(30,2,230),单分手数少(1000,500,9000),流值小于(100,5,900);
收价:=CLOSE;
五均:=(CLOSE+"分爆引用.昨日四价和#DAY")/5;  # close是动态更新的，是否会遇到5均线止损一样的问题
十均:=(CLOSE+"分爆引用.昨日九价和#DAY")/10;
踏上双线:=CLOSE>五均 AND CLOSE>十均;
开幅:=(DYNAINFO(4)-DYNAINFO(3))/DYNAINFO(3)*100;
涨跌:=(CLOSE-DYNAINFO(3))/DYNAINFO(3)*100;
开冲砸:=开幅<=开幅上限 AND 开幅>=开幅下限 AND REF(HHV(涨跌,0)<=冲高至多 AND LLV(涨跌,0)>=下砸底限,1);
高距今:=REF(HHVBARS(CLOSE,0),1)+1;
前高价:=REF(CLOSE,高距今);
TTT:=SUM(VOL,0)/"分爆引用.昨日四价和#DAY";
量返回:=IF(TIME/100>=931 AND TIME/100<=1000,TTT>=0.25,IF(TIME/100>1000 AND TIME/100<=1129,TTT>=0.33,IF(TIME/100>=1301 AND TIME/100<=1457,TTT>=0.67,0)));
突破:=TTT AND 踏上双线 AND VOL>=单分手数少 AND 涨跌>=1 AND CLOSE>前高价*1.001 AND 高距今>=间隔分钟至少 AND 开冲砸 AND CAPITAL/1000000*CLOSE<=流值小于;
有过突:COUNT(突破,0);
```

##### 分时爆点(投入使用中）
```
INPUT:开幅上限(3,-9,9),开幅下限(-2,-9,9),冲高至多(5,-9,9),下砸底限(-3,-9,9),间隔分钟至少(30,2,230),单分手数少(1000,500,9000);  # 1分钟手数至少？
收价:CLOSE,COLORWHITE,LINETHICK2,PRECIS2;  # 赋予变量的同时，在图上画出线
五均:(CLOSE+"分爆引用.昨日四价和#DAY")/5,COLORWHITE,DOTLINE;
十均:(CLOSE+"分爆引用.昨日九价和#DAY")/10,COLORFF00FF,DOTLINE;
踏上双线:=CLOSE>五均 AND CLOSE>十均;
开幅:=(DYNAINFO(4)-DYNAINFO(3))/DYNAINFO(3)*100;  # 今开相对于昨收
涨跌:=(CLOSE-DYNAINFO(3))/DYNAINFO(3)*100;  # 当前价相对于昨收，CLOSE会动态变化
开冲砸:开幅<=开幅上限 AND 开幅>=开幅下限 AND REF(HHV(涨跌,0)<=冲高至多 AND LLV(涨跌,0)>=下砸底限,1),LINETHICK0,PRECIS0;
高距今:REF(HHVBARS(CLOSE,0),1)+1,LINETHICK0,PRECIS0;
前高价:REF(CLOSE,高距今),LINETHICK0,PRECIS2;
TTT:=SUM(VOL,0)/"分爆引用.昨日四价和#DAY";
量返回:IF(TIME/100>=931 AND TIME/100<=1000,TTT>=0.25,IF(TIME/100>1000 AND TIME/100<=1129,TTT>=0.33,IF(TIME/100>=1301 AND TIME/100<=1457,TTT>=0.67,0))),LINETHICK0,PRECIS0;
突破:TTT AND 踏上双线 AND VOL>=单分手数少 AND 涨跌>=1 AND CLOSE>前高价*1.001 AND 高距今>=间隔分钟至少 AND 开冲砸,LINETHICK0,PRECIS0;
有过突:COUNT(突破,0),LINETHICK0,PRECIS0;
DRAWTEXT(突破,CLOSE*1.008,'突'),COLORYELLOW,LINETHICK2;
{9:30-10：00 成交量是昨天的4分之一以上 
10：00- 11：30 成交量是昨天的 3分之一 以上 
1:00-3：00 成交量是昨天的3分之2以上};
```

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