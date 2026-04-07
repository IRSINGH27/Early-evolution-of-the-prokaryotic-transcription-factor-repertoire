
class FirstGain:
    def __init__(self, extantFile: str, asrFile: str,treeFile:str, firstGainFile: str, ncores: int):
        self.allTreeData,self.pathDict = self.preparationTreeFiles(extantFile=extantFile,asrFile=asrFile,treeFile=treeFile)
        self.firstGainFile = firstGainFile
        self.ncores = ncores

    def writer(self):
        with open(self.firstGainFile,'w') as f:
            f.write(f'Path\tGroup\tgainNode\n')
            result= self.worker()
            for items in result:
                if items:
                    try:
                        path,group,node=items #type:ignore
                    except:
                        print(items)
                        raise Exception
                    f.write(f'{path}\t{group}\t{node}\n')
        return None
    
    def writer_overrall(self):
        with open(self.firstGainFile,'w') as f:
            f.write(f'Path\tGroup\tgainNode\n')
            result= self.worker()
            for items in result:
                if items:
                    # for item2 in items:
                    path,group,node=items #type:ignore
                    f.write(f'{path}\t{group}\t{node}\n')
        return None
    def argumentMaker(self,test=False):
        from itertools import product
        if test:
            self.arguments = [('Path_ 1', '33JYR'), ('Path_ 1', '30SDS'), 
                          ('Path_ 1', 'arCOG08271'), ('Path_ 1', 'COG1530')]
        else:
            paths=list(self.pathDict.keys())
            groups=list(self.allTreeData.keys())
            arguments=list()
            arguments=product(paths,groups)
            self.arguments=[(path,group,self.pathDict,self.allTreeData) for path,group in arguments]
        return None
    
    def worker(self,firstGain=True):
        import multiprocessing as mp

        self.argumentMaker(test=False)
        print('arguments are ready now starting the multiprocessing')            
        with mp.Pool(self.ncores) as pool:
            results = pool.starmap(self.firstGainprocess, self.arguments)
        # print(results)
        return results
    
    @staticmethod
    def firstGainprocess(path: str, group: str,pathDict:dict,allTreeData:dict):
        for node in pathDict[path]:
            if allTreeData[group].get(node, None):
                return path, group, node
        return None
    
    @staticmethod
    def retentionNode(path:str,group:str,pathDict:dict,allTreeData:dict):
        gain=False
        gainNode=-1
        for node in pathDict[path]:
            if not gain :
                if allTreeData[group].get(node,False) is True:
                    gain=True
                    gainNode=node
            else:
                if allTreeData[group].get(node,False) is False:
                    return path,group,gainNode,node
        return path,group,gainNode,-1
                
    @staticmethod
    def overallGainProcess(path: str, group: str,pathDict:dict,allTreeData:dict):
        results=[]
        check=True
        for node in pathDict[path]:
            if check:
                if allTreeData[group].get(node, False):
                    results.append((path,group,node))
                    check=False
            else:
                if not allTreeData[group].get(node, False):
                    check=True
        return results
    
    def preparationTreeFiles(self,extantFile:str,asrFile:str,treeFile:str):
        import pandas as pd
        extantData=pd.read_csv(extantFile,sep='\t',index_col=0)
        extantData.columns=[i.replace('X','',1) if i[0]=='X' else i.split('.')[0] for i in extantData.columns]
        asrData=pd.read_csv(asrFile,sep='\t',index_col=0)
        asrData.columns=[i.split('_')[0] for i in asrData.columns]
        asrData.columns=[i.replace('X','',1) if i[0]=='X' else i.split('.')[0] for i in asrData.columns]
        treeDF=pd.read_csv(treeFile,sep='\t',index_col=0)
        treeDF['path']=treeDF['path'].apply(lambda x:tuple(list(map(int,x.split(',')))))
        extantData=extantData.loc[treeDF.index.unique()]
        extantData.index=treeDF["node"].values #type:ignore
        extantData.index.name='node' #type:ignore
        extantData.columns=[i.split('.')[0] for i in extantData.columns]
        extantData=extantData.loc[:,asrData.columns.values] #type:ignore
        asrData.index.name='node'
        extantData=extantData.loc[:,asrData.columns]
        allData=pd.concat([asrData,extantData],axis=0).astype(bool)
        pathDict=treeDF.set_index('PathID')['path'].to_dict()
        allTreeData=allData.to_dict()
        return allTreeData,pathDict


def main(configFile:str):
    from json import load
    from pprint import pprint
    with open(configFile,'r') as f:
        config=load(f)
    extantFile=config['extantFile']
    asrFile=config['asrFile']
    treeFile=config['treeFile']
    firstGainFile=config['firstGainFile']
    ncores=config.get('ncores',1)
    print('config Read')
    pprint(config,compact=True)
    classWorker=FirstGain(extantFile=extantFile,asrFile=asrFile,treeFile=treeFile,firstGainFile=firstGainFile,ncores=ncores) #type:ignore
    classWorker.writer()
    return None


if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='calculate first gain from extant asr and tree file')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
