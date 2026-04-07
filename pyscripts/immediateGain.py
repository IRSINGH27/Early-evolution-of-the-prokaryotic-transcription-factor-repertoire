class LocalRate:
    __slots__=['nodeCOG','pathDict','arguments']
    def __init__(self,extantFile:str,asrFile:str,treeFile:str):
        self.nodeCOG,self.pathDict=self.prepareData(extantFile,asrFile,treeFile)
        return None
    
    def worker(self,path:str,nodeCOG:dict,pathDict:dict):
        parentPath=pathDict[path]
        result={}
        for _index,parentNode in enumerate(parentPath):
            parentOGs=nodeCOG[parentNode]
            for childNode in parentPath[_index+1:]:
                childOGs=nodeCOG[childNode]
                result[childNode]=self.novelGainAncestorCalculator(parentOG=parentOGs,childOG=childOGs)
                # result[childNode]=self.rateCalculator(parentOG=parentOGs,childOG=childOGs)
        return result

    def argumentMaker(self,test=False):
        if test:
            from random import sample
            self.arguments=[(path,self.nodeCOG,self.pathDict) for path in sample(list(self.pathDict.keys()),min(10,len(self.pathDict)))]
        else:
            self.arguments=[(path,self.nodeCOG,self.pathDict) for path in self.pathDict.keys()]
        return None
    
    def multiWorker(self,ncores:int):
        from multiprocessing import Pool
        self.argumentMaker()
        result={}
        with Pool(ncores) as pool:
            temp=pool.starmap(self.worker,self.arguments)
        for nodeDict in temp:
            for node in nodeDict:
                if node not in result:
                    result[node]=nodeDict[node]
        return result
    
    def writer(self,data:dict,output:str):
        with open(output,'w') as slave:
            check=True
            for node in data:
                d = data[node]
                if check:
                    header="\t".join(list(d.keys()))
                    slave.write(f'Node\t{header}\n')
                    check=False
                content='\t'.join(list(map(str,d.values())))
                slave.write(f"{node}\t{content}\n")
        return None
      
    @staticmethod
    def prepareData(extantFile:str,asrFile:str,treeFile:str):
        from pandas import read_csv,concat
        extantData=read_csv(extantFile,sep='\t',index_col=0)
        extantData.columns=[i.split('.')[0] for i in extantData.columns]
        extantData.columns=[i.replace('X','',1) if i.startswith('X') else i for i in extantData.columns]
        asrData=read_csv(asrFile,sep='\t',index_col=0)
        asrData.columns=[i.split('_l',1)[0] for i in asrData.columns]
        treeDF=read_csv(treeFile,sep='\t',index_col=0)
        treeDF['path'] = treeDF['path'].apply(lambda x: tuple(map(int, x.split(','))))
        extantData=extantData.loc[treeDF.index.unique()]
        extantData.index=treeDF["node"].values #type:ignore
        extantData.index.name='node'
        asrData.index.name='node'
        asrData.index=asrData.index.astype(int)
        extantData.index=extantData.index.astype(int)
        if asrData.shape[1]!=extantData.shape[1]:
            extantData=extantData.loc[:,asrData.columns]
            print(extantData.shape)
        allData=concat([asrData,extantData],axis=0).astype(bool)
        nodeCOG={}
        for node in allData.index:
            nodeCOG[node] = set(allData.columns[allData.loc[node].values])
        pathDict=treeDF.set_index('PathID')['path'].to_dict()
        print(1)
        return nodeCOG,pathDict

    @staticmethod
    def rateCalculator(parentOG:set,childOG:set):
        gainFraction=None
        lossFraction=None
        retainFraction=None
        if (len(parentOG)!=0) and (len(childOG)!=0):
            gainFraction=len(childOG-parentOG)/len(parentOG)
            lossFraction=len(parentOG-childOG)/len(parentOG)
            retainFraction=len(parentOG.intersection(childOG))/len(parentOG)
        elif len(parentOG)!=0:
            lossFraction=1
        elif len(childOG)!=0:
            gainFraction=1
        return {'gainFraction':gainFraction,
                'lossFraction':lossFraction,
                'retainFraction':retainFraction}

    @staticmethod
    def novelGainAncestorCalculator(parentOG:set,childOG:set):
        novelGain=None
        parentLoss=None
        retain=None
        if (len(parentOG)!=0) and (len(childOG)!=0):
            novelGain=len(childOG-parentOG)
            parentLoss=len(parentOG-childOG)
            retain=len(parentOG.intersection(childOG))
        elif len(parentOG)!=0:
            parentLoss=len(parentOG)
        elif len(childOG)!=0:
            novelGain=len(childOG)
        return {'novelGain':novelGain,
                'parentLoss':parentLoss,
                'retain':retain}
    @staticmethod
    def gainsCalculator(parentOG:set,childOG:set):
        gainCount=0
        if (len(parentOG)!=0) and (len(childOG)!=0):
            gainCount=len(childOG-parentOG)
        elif len(childOG)!=0:
            gainCount=len(childOG)
        return gainCount


def main(configFile:str):
    from json import load
    from pprint import pprint
    with open(configFile,'r') as f:
        config=load(f)
    pprint(config)
    extantFile=config['extantFile']
    asrFile=config['asrFile']
    treeFile=config['treeFile']
    outputFile=config['outputFile']
    ncores=config.get('ncores',1)
    classWorker=LocalRate(extantFile=extantFile,asrFile=asrFile,treeFile=treeFile) #type:ignore
    data=classWorker.multiWorker(ncores=ncores)
    classWorker.writer(data=data,output=outputFile)
    return None


if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='Calculate local Rate')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
