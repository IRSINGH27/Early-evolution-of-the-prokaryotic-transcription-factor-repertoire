def cogNodeDataReader(file:str,threshold:float) :
    from os.path import basename
    from pandas import read_csv
    df=read_csv(file,sep='\t',index_col=0)
    if df.shape[-1]==1:
        if '0' in df.columns:
            df['1']=1-df['0']
            df=df.loc[:,['0','1']]
        else:
            df['0']=1-df['1']
            df=df.loc[:,['0','1']]
    df.columns=['Abs','Prs']
    df=df[['Prs']]>=threshold
    if basename(file)[0:2]=='_X':
        cogName=basename(file).replace('_X','',1)
    else:
        cogName=basename(file).replace('_','',1)
    cogName=cogName.split('_asr')[0]
    df.columns=[cogName]
    df.index=df.index.astype(int)
    return df


def multiWorker(folder:str,threshold:float,ncores:int) :
    from multiprocessing import Pool
    from os import path,listdir
    from pandas import concat
    arguments=[(path.join(folder,file),threshold) for file in listdir(folder) if '_likanc.tsv' in file]
    with Pool(ncores) as pool:
        listofCOGASRs=pool.starmap(cogNodeDataReader,arguments)
    result=concat(listofCOGASRs,axis=1) #type:ignore
    print(result)
    return result

def main(configFile:str) -> None:
    from json import load
    with open(configFile,'r') as f:
        config=load(f)
    print(config)
    content=multiWorker(config['folder'],config.get('threshold',.75),config.get('ncores',1))
    content.astype(int).to_csv(config['output'],sep='\t') #type:ignore
    return None

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='take asr result for indv cog and  make single file')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)