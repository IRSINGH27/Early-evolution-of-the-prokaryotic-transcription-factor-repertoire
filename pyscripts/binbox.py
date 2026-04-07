import pandas as pd
def reader(file:str):
    df=pd.read_csv(file,sep='\t',index_col=0)
    return df

def nodeMaker(distanceFile:str,root:int):
    from numpy import arange
    distanceMatrix=reader(distanceFile)
    distanceMatrix.columns=distanceMatrix.index.values
    distanceMatrix=distanceMatrix.loc[root]
    maxDistance=distanceMatrix.max()
    std=distanceMatrix.std()
    bins={}
    distanceList=arange(0,maxDistance-(std/2),std/2)
    for count,i in enumerate(distanceList):
        min_distance,max_Distance=round(i,6),round(i+(std/2),6)
        if (count+1) == len(distanceList):
            max_Distance=maxDistance
        node=distanceMatrix[(distanceMatrix>=min_distance) & (distanceMatrix<max_Distance)].index.values
        if node.shape[0]>0:
            bins[f'Bin_{count+1}']=node
    return bins

def dataAdder(dataFile:str,binDict:dict,nodeColumnName:str,TF:bool,tfFile=None):
    data=reader(dataFile)
    if isinstance(tfFile,str):
        tf=reader(tfFile)
        tfList=tf[tf.Status=='TF'].index.unique()
        ntfList=list(set(data.OG.unique())-set(tfList))
        if TF:
            iOG=tfList
        else:
            iOG=ntfList
    data=data[data.OG.isin(iOG)]
    data=data.value_counts(nodeColumnName)
    data.index.name='node'
    data.columns=['Count']
    # return data
    result={}
    count=0
    for bins,node in binDict.items():
        commonNode=list(set(data.index.unique().tolist()).intersection(node))
        val=data[commonNode].astype(str).values
        if val.shape[0]>0:
            result[count]={'Bins':bins,'Count':','.join(val)}
        count+=1
    result=pd.DataFrame(result).T.set_index('Bins')
    result['Count']=result['Count'].apply(lambda x:list(map(int,x.split(','))))
    result=result.explode(['Count'])
    return result

def test():
    distanceFile='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/finalTree/16s_GTDB/trees/workingFiles/16SrRNA.pruned.tree_1.distanceMatrix'
    root=2646
    dataFile='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/HTH/compiledFiles/16s/tree_1/PathWay_level_FirstGainFile.tsv'
    tfFile='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/HTH/Results/hmmscan/TF_Aswin/Potential_TF_OG.tsv'
    binDict=nodeMaker(distanceFile=distanceFile,root=root)
    binData=dataAdder(dataFile=dataFile,binDict=binDict,nodeColumnName='Node',TF=True,tfFile=tfFile)
    return binData

def main(configFile:str):
    from json import load
    from pprint import pprint
    with open(configFile,'r') as f:
        config=load(f)

    pprint(config)
    distanceFile=config['distanceFile']
    root=config['root']
    dataFile=config['dataFile']
    tfFile=config['tfFile']
    TF=config.get('TF',True)
    nodeColumnName=config.get('nodeColumnName','Node')
    dataColumn=config.get('dataColumn','OG')
    binDict=nodeMaker(distanceFile=distanceFile,root=root)
    binData=dataAdder(dataFile=dataFile,binDict=binDict,nodeColumnName=nodeColumnName,TF=TF,tfFile=tfFile)
    binData.to_csv(config['output'],sep='\t')

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
