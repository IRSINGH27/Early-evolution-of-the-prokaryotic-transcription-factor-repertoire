def filterDF(fileName:str,znbr:bool):
    from math import log2
    import pandas as pd
    import re
    orgName=re.findall(r'GC[AF]_\d+',fileName)[0]
    df=pd.read_csv(fileName,sep='\t',index_col=0)
    if znbr:
        thresholdScore=log2(0.999/(1-0.999))
        df=df[(df['E-value']<=.001) & (df['score']>=thresholdScore)]
    else:
        df=df[df['score']>0]
        df=df[(df['E-value']<=.001)]
    if df.empty:
        return None
    else:
        df['OrgName']=orgName
        df['query_name']=orgName+'|'+df['query_name']
        df=df.sort_values('score',ascending=False)
        df=df.drop_duplicates('query_name')
        df=df.set_index('query_name')
        return df

def worker(_input_:str,znbr:bool,_output_:str):
    df=filterDF(_input_,znbr=znbr)
    if df.empty: #type:ignore
        return None
    else:
        df.to_csv(_output_,sep='\t') #type:ignore
    return None
    

def multiWorker(inputFolder:str,znbr:bool,outputFolder:str,ncores:int):
    from multiprocessing import Pool
    from os import listdir,path
    argument=[(path.join(inputFolder,i),znbr,path.join(outputFolder,i.split('.',1)[0]+'.filtered.tsv')) for i in listdir(inputFolder)]
    with Pool(ncores) as pool:
        pool.starmap(worker,argument)
    return None

def main(configFile:str):
    from json import load
    from os import path,makedirs
    with open(configFile, 'r') as config_file:
        config = load(config_file)
    __input__ = config['inputFolder']
    __output__ = config['outputFolder']
    __ncores__=config.get('ncores',1)
    znbr = config.get('znbr',False)
    print(f"Arguments {__input__}\t{__output__}\t{__ncores__}\t{znbr}")
    if not path.exists(__output__):
        makedirs(__output__)
    multiWorker(inputFolder=__input__,outputFolder=__output__,ncores=__ncores__,znbr=znbr)
    return None


if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='concat all protein files into single file making header with file name and protein name')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)