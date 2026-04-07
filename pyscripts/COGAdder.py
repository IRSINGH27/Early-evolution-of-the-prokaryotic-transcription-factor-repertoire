import pandas as pd

def reader(file:str,parquet:bool):
    if not parquet:
        df=pd.read_csv(file,sep='\t',index_col=0,nrows=100)
        if df.index.name=='query_name':
            df=df.reset_index()
        return df.T.to_dict()
    else:
        df=pd.read_parquet(file)
        df.set_index('proteinName',inplace=True)
        return df

def argumentMaker(cogFile:str,filterFile:str):
    dfDict=reader(filterFile,False)
    dfCOG=reader(cogFile,True)
    arguments=[(i,k,dfCOG) for i,k in dfDict.items()]
    return arguments

def worker(rowIndex:int,rowData:dict,dfCOG:pd.DataFrame):
    if rowData['query_name'] in dfCOG.index:
        targetCOG=dfCOG.loc[rowData['query_name'],'target_name']
        if type(targetCOG)!=str:
            targetCOG='|'.join(targetCOG.unique())
    else:
        targetCOG='-'
    rowData.update({'COG':targetCOG})
    return {rowIndex:rowData}

def multiWorker(arguments:list,ncores:int):
    from multiprocessing import Pool
    with Pool(ncores) as pool:
        result=pool.starmap(worker,arguments)
    temp={i:k for d in result for i,k in d.items()}
    return temp

def writer(dfDict:dict,output:str):
    with open(output,'w') as f:
        check=True
        for rowIndex,rowDict in dfDict.items():
            content='\t'.join(list(map(str,list(rowDict.values()))))
            if check:
                header='\t'.join(list(rowDict.keys()))+'\n'
                content=header+content+'\n'
                check=False
            else:
                content=content+'\n'
            f.write(content)

def main(configFile:str):
    from json import load
    with open(configFile,'r') as f:
        config=load(f)
    dfFile=config['dfFile']
    cogFile=config['cogFile']
    ncores=config.get('ncores',1)
    output=config.get('output','output.tsv')
    arguments=argumentMaker(cogFile,dfFile)
    print('argument Made')
    resultDict=multiWorker(arguments,ncores)
    writer(resultDict,output)
    return None

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='calculate first gain from extant asr and tree file')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
