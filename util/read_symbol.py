import pandas as pd

def read_symbol(file_path,sheet_name):
    '''
    return: a list of strings
    '''
    
    info=pd.read_excel(file_path,sheet_name,index_col=0)
    info.index=info.index.astype('str')
    symbol=info.index.to_list()
    symbol=['0'*(6-len(i))+i for i in symbol]
    
    return symbol
    
if __name__ == "__main__":
    symbol=read_symbol('券源汇总.xlsx','券源数量')
