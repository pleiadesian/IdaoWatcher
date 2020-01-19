# TdxPlugin
code for tdx plugin. Generate dlls to carry out my trading strategy.

## DLL函数编程规范
### DLL函数结构

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
