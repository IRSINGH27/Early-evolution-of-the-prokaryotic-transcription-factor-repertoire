class EntroCalculator:
    def __init__(self, asrFile: str, cog2sfFile: str, ncores: int):
        self.asrCOGDict, self.cog2sfDict = self.prepareVariables(asrFile, cog2sfFile)
        self.ncores = ncores

    def prepareVariables(self, asrFile, cog2sfFile):
        import pandas as pd # type: ignore
        asrDict = pd.read_csv(asrFile, sep='\t', index_col=0)
        asrDict.columns=[i.split('_')[0] for i in asrDict.columns]
        asrDict=asrDict.astype(bool).T.to_dict()
        cog2sfDF = pd.read_csv(cog2sfFile, sep='\t')
        cog2sfDF.columns = ['cog', 'ssf']
        cog2sfDF = cog2sfDF[~cog2sfDF['ssf'].str.startswith('P')]
        cog2sfDict = {}
        for sf, subdf in cog2sfDF.groupby('ssf'):
            cog2sfDict[sf] = subdf['cog'].tolist()
        return asrDict, cog2sfDict

    def multiWorker(self):
        from multiprocessing import Pool
        args = [(node, self.asrCOGDict, self.cog2sfDict) for node in self.asrCOGDict]
        print('multiworker started')
        with Pool(self.ncores) as pool:
            results = pool.starmap(sf_worker2, args)
        return dict(results)


def sf_worker(node: int, asrCOGDict: dict, cog2sfDict: dict):
    nodeCogCounts = asrCOGDict[node]

    presentSFs = []

    for sf, cogList in cog2sfDict.items():
        val = sum(nodeCogCounts.get(cog, False) for cog in cogList)
        if val > 0:
            presentSFs.append(sf)

    if not presentSFs:
        return node, '-'   

    return node, '|'.join(presentSFs)

def sf_worker2(node: int, asrCOGDict: dict, cog2sfDict: dict):
    nodeCogCounts = asrCOGDict[node]

    presentSFs = {}

    for sf, cogList in cog2sfDict.items():
        val = sum(nodeCogCounts.get(cog, False) for cog in cogList)
        if val > 0:
            presentSFs[sf]=val

    # Special case: node has no SFs (and effectively no COGs)
    if not presentSFs:
        return node, {'-':0}  # marker for empty node
    return node,presentSFs


def entropy_worker(node:int, asrCOGDict:dict, cog2sfDict:dict):
    from numpy import log # type: ignore
    nodeCogCounts = asrCOGDict[node]
    presentCogSF = {}
    for sf, cogList in cog2sfDict.items():
        val = sum(nodeCogCounts.get(cog, False) for cog in cogList)
        if val > 0:
            presentCogSF[sf] = val
            
    total_count = sum(presentCogSF.values())
    K = len(presentCogSF)
    if total_count == 0:
        return node,-1
    if K <= 1:
        return node, 0
    entropy = 0.0
    for count in presentCogSF.values():
        p = count / total_count
        entropy += p * log(p)
    entropy = -entropy / log(K)
    return node, entropy

def main(configFile:str):
    from json import load,dump
    import pandas as pd
    from numpy import log
    with open(configFile) as f:
        config=load(f)
    asrFile=config['asrFile']
    cog2sfFile=config['cog2sfFile']
    ncores=config.get('ncores',1)
    entro=EntroCalculator(asrFile=asrFile,cog2sfFile=cog2sfFile,ncores=ncores)
    result=entro.multiWorker()
    result=pd.DataFrame.from_dict(result).T.fillna(0)
    print(result)
    en=result.apply(lambda x:x/result.sum(axis=1)*log(x/result.sum(axis=1))).fillna(0).sum(axis=1)*-1
    print(result)
    entropy=pd.DataFrame(en/log(result.astype(bool).sum(axis=1)))
    entropy.to_csv(config.get('output','output.df'),sep='\t')
    # with open(config.get('output','output.json'),'w') as f:
    #     dump(result,f)
    # with open(config.get('output','output.tsv'),'w') as f:
    #     f.write('Node\tEntropy\n')
    #     for node,entropy in result.items():
    #         f.write(f'{node}\t{entropy}\n')
    return None

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='Entro Calculator')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)