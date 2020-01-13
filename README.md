# IdaoWatcher
### 正在测试的功能
* 监听封板股，若出现开板迹象则发出警告


# TdxPlugin
以下是通达信插件编程规范的说明。因为目前通达信接口所能提供的实时信息太少，暂时不考虑使用通达信插件实现交易策略。

### Plugin_function编程规范
* PluginTCal用于生成tdx中可以调用的函数
---

* PluginTCalcFunc.h头文件
```c
#ifndef __PLUGIN_TCALC_FUNC
#define __PLUGIN_TCALC_FUNC
#pragma pack(push,1) 

//函数(数据个数,输出,输入a,输入b,输入c)
typedef void(*pPluginFUNC)(int,float*,float*,float*,float*);

typedef struct tagPluginTCalcFuncInfo
{
	unsigned short		nFuncMark;//函数编号
	pPluginFUNC			pCallFunc;//函数地址
}PluginTCalcFuncInfo;

typedef BOOL(*pRegisterPluginFUNC)(PluginTCalcFuncInfo**);  

#pragma pack(pop)
#endif
```

* 包括注册DLL函数基本信息
注册函数名称为RegisterTdxFunc。具体函数实例可参见TCalcFuncSets.cpp示范程序。<br>
```c
//加载的函数
PluginTCalcFuncInfo g_CalcFuncSets[] = 
{
	{1,(pPluginFUNC)&TestPlugin1},
	{2,(pPluginFUNC)&TestPlugin2},
	{0,NULL},
};

//导出给TCalc的注册函数
BOOL RegisterTdxFunc(PluginTCalcFuncInfo** pFun)
{
	if(*pFun==NULL)
	{
		(*pFun)=g_CalcFuncSets;
		return TRUE;
	}
	return FALSE;
}
```

* 细节说明
  * PluginTCalcFunc.h头文件中PluginTCalcFuncInfo结构用来存放用户自己的函数pCallFunc和函数唯一标记nFuncMark
  * pCallFunc是typedef void(*pPluginFUNC)( int DataLen,float* pfOUT,float* pfINa,float* pfINb,float* pfINc)类型指针
  * 函数参数分别是(数据个数,输出,输入a,输入b,输入c),参数的计算是基于长度为DataLen 的float类型数组
  * RegisterTdxFunc函数为注册函数，用户的函数全部都放入PluginTCalcFuncInfo结构的全局数组g_CalcFuncSets中
  
### Plugin_select编程规范
* MyPlugin用于生成tdx中调用筛选的插件
---
* 插件信息注册函数
	* 包括注册插件基本信息和参数信息，相关结构定义参见OutStruct.h，现支持4个参数。
	* 具体函数实例可参见MyPlugin.cpp示范程序。
	
* 筛选条件判断函数
* 此函数申请全部本地历史数据判断最新条件成立与否。
```c
BOOL InputInfoThenCalc1(char *Code,short nSetCode,int Value[4],short 
DataType,short nDataNum,BYTE nTQ,unsigned long unused);
```
* 此函数阶段的历史判断计算阶段最后条件成立与否。
```c
BOOL InputInfoThenCalc2(char * Code,short nSetCode,int Value[4],short 
DataType,NTime time1,NTime time2,BYTE nTQ,unsigned long unused)
```
* 数据申请是通过函数指针调用回调函数，该回调函数声明如下：
```c
typedef long(CALLBACK * PDATAIOFUNC)(char * Code,short nSetCode,short 
DataType,void * pData,short nDataNum,NTime,NTime,BYTE nTQ,unsigned long);
```
* 参数说明
	* Code为代码，如申请上证数据则赋值为999999
	* nSetCode为市场分类，0为深，1为沪
	* DataType为申请数据类型，缺省为历史数据，如申请行情数据则赋值为REPORT_DAT2，其他相关类型参见OutStruct.h
	* pData为申请数据缓冲区，若为NULL且nDataNum为-1则函数返回历史数据个数
	* nDataNum为申请数据个数，若为-1且pData为NULL则函数返回历史数据个数
	* 2个Ntime为申请数据的时间范围，缺省为全部本地历史数据
	* nTQ是否为精确除权

* 注意
	* 应考虑判断申请到的数据个数
	* 函数编写应注意判断数据的有效性，系统对{0xF8,0xF8,0xF8,0xF8}定义为无效数，对无效数应加以判断不参与计算
	
### 模块
* standOnDailyLimit
* yesterdaySafe
* yesterdayOnNeck
	* neckline的计算
