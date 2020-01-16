// choice1.cpp : Defines the entry point for the DLL application.
// 插件实例

#include "stdafx.h"
#include "plugin.h"
#include <stdio.h>
#include <stdlib.h>

#define PLUGIN_EXPORTS

BOOL APIENTRY DllMain(HANDLE hModule,
DWORD  ul_reason_for_call,
        LPVOID lpReserved
)
{
switch (ul_reason_for_call)
{
case DLL_PROCESS_ATTACH:
case DLL_THREAD_ATTACH:
case DLL_THREAD_DETACH:
case DLL_PROCESS_DETACH:
break;
}
return TRUE;
}

PDATAIOFUNC	 g_pFuncCallBack;

//获取回调函数
void RegisterDataInterface(PDATAIOFUNC pfn)
{
    g_pFuncCallBack = pfn;
}



//注册插件信息
void GetCopyRightInfo(LPPLUGIN info)
{
    //填写基本信息
    strcpy(info->Name, "三一股");
    strcpy(info->Dy, "Wenling");
    strcpy(info->Author, "IDAO");
    strcpy(info->Period, "隔日交易");
    strcpy(info->Descript, "0.日K曾涨停（standonDailyLimit）1.昨日收阴/十字星（yesterdaySafe） 2.历史重要颈线位");
    strcpy(info->OtherInfo, "自定义");
    //填写参数信息 考虑用参数表示想要选择的三一股的强弱

    info->ParamNum = 1;
    strcpy(info->ParamInfo[0].acParaName, "日K考察范围（3天-200天）");
    info->ParamInfo[0].nMax = 3;
    info->ParamInfo[0].nMax = 200;
    info->ParamInfo[0].nDefault = 10;
}

////////////////////////////////////////////////////////////////////////////////
//自定义实现细节函数(可根据选股需要添加)

const	BYTE	g_nAvoidMask[] = { 0xF8,0xF8,0xF8,0xF8 };	// 无效数据标志(系统定义)


BOOL standOnDailyLimit(float* price, long max) {
    float lowest = 100;
    for (int i = 0; i < max; i++) {
        if (i > 0) {
            float increase = (price[i] - price[i - 1]) / price[i - 1];
            if (increase > 0.095) {  //判断涨停
                lowest = price[i - 1] < lowest ? price[i - 1] : lowest;
            }
        }
    }
    if (lowest < price[max - 1]) return TRUE;
    else return FALSE;
}

//60分钟周期安全，定量定义十字星
BOOL yesterdaySafe(HISDAT pHisDat) {
    // 昨日收阳3个点且未冲高回落，不符
    if (pHisDat.Close > pHisDat.Open * 1.03 && !pHisDat.High < pHisDat.Open * 1.07) {
        return FALSE;
    }
    return TRUE;
}

// append new line at the end, or increase the num of corresponding line
void appendLine(Neckline *neckline,float assumeP) {
    for (int i = 0; i < neckline->index; i++) {
        if (neckline->neck_price[i] - assumeP < 0.000001 && neckline->price[i] - assumeP > -0.000001) {
            neckline->neck_price_amount[i]++;
            return;
        }
    }
    neckline->index++;
    neckline->neck_price[neckline->index]=assumeP;

}

Neckline calcNeckline(float* price, long max) {
    // 记录每一个拐点(考虑使用递归，区分出横向盘整情况）
    // 横向盘整处形成颈线
    // 目前以5个点以上且两天以上的单向走势作为有效走势
    Neckline possiblePoint, neckline, returnNeckline;
    float rised = 0;
    float maxP = price[0];
    float minP = price[0];

    // 计算拐点和最大最小值
    for (int i = 1; i < max; i++)
    {
        if (rised * (price[i] - price[i - 1]) < 0) {
            possiblePoint.price[possiblePoint.index] = price[i - 1];
            possiblePoint.index++;
        }
        rised = price[i] - price[i - 1];
        maxP = maxP > price[i] ? maxP : price[i];
        minP = minP < price[i] ? minP : price[i];
    }

    // neckline to iterate through possible turning point
    // magic number to be fixed. 1. areas:20  2. amplitude:0.01
    for (int i = 0; i < 20; i++) {
        float assumeP = maxP - (maxP - minP) * i / 20;
        float upperBound = assumeP * 1.01;
        float lowerBound = assumeP * 0.99;
        for (int j = 0; j <= possiblePoint.index; j++) {
            appendLine(&neckline, assumeP);
        }
    }

    for (int i = 0; i < neckline.index;i++) {
        if(neckline.neck_price_amount[i] > 5) {  // 5: min num of turning point falls on neckline
            appendLine(&returnNeckline, neckline.neck_price[i]);
        }
    }
    return returnNeckline;
}


BOOL yesterdayOnNeckline(float *price,long max) {
    Neckline neckline = calcNeckline(price, max);
    for (int i = 0;i < neckline.index; i++) {
        if (price[max-1] < price[i]*1.01 && price[max-1] > price[i]* 0.99)
            return TRUE;
    }
    return FALSE;
}


BOOL InputInfoThenCalc1(char* Code, short nSetCode, int Value[4], short DataType, short nDataNum, BYTE nTQ, unsigned long unused) //按最近数据计算
{
    BOOL nRet = FALSE;
    NTime tmpTime = { 0 };
    BOOL condition[2];// index说明对应description
    LPHISDAT pHisDat = new HISDAT[nDataNum];  //数据缓冲区 每个hisdat为一根k线的所有信息
    long readnum = g_pFuncCallBack(Code, nSetCode, DataType, pHisDat, nDataNum, tmpTime, tmpTime, nTQ, 0);  //利用回调函数申请数据，返回得到的数据个数
    if (readnum > max(Value[0], Value[1])) //只有数据个数大于Value[0]和Value[1]中的最大值才有意义
    {
        float* price = new float[readnum];
        for (int i = 0; i < readnum; i++) //将收盘价导入数组
        {
            price[i] = pHisDat[i].Close;
        }

        condition[0] = standOnDailyLimit(price, readnum);
        condition[1] = yesterdaySafe(pHisDat[readnum - 1]);
        condition[2] = yesterdayOnNeckline(price, readnum);

    }

    if (condition[0] || condition[1]) nRet = TRUE;
    delete[]pHisDat; pHisDat = NULL;
    return nRet;
}
