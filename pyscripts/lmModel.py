import pandas as pd
from numpy import log10



class LMModel:
    def __init__(self,extantControlFile:str,asrControlFile:str,extantOGFile:str,asrOGFile:str,distanceFile:str,phylumFile:str,treePathFile:str,tfFile:str):

        self.tfList=self.tfListPreparotr(tfFile=tfFile)

        self.bacterial_node,self.extantDF,self.distanceMatrix,self.root=self.extantFilePreparator(controlFile=extantControlFile,hthFile=extantOGFile,phylumFile=phylumFile,distanceFile=distanceFile,treePathFile=treePathFile)
        self.asrDF=self.asrFilePrepartor(controlFile=asrControlFile,hthFile=asrOGFile)
    
    def worker(self):
        self.model=self.modelTrainer()
        self.extantDF=self.predictorModel(self.model,self.extantDF)
        self.asrDF=self.predictorModel(self.model,self.asrDF)
        commonCol=list(set(self.asrDF.columns).intersection(self.extantDF.columns))
        df=pd.concat([self.extantDF,self.asrDF.loc[:,commonCol]])
        return df

    def extantFilePreparator(self,controlFile:str,hthFile:str,phylumFile:str,distanceFile:str,treePathFile:str,):
        extantControl=self.reader(controlFile)
        hthDF=self.reader(hthFile)
        phylumInfo=self.reader(phylumFile)
        distanceMatrix=self.reader(distanceFile)
        treePath=self.reader(treePathFile)
        bacterial_node=[]

        extantControl=extantControl.loc[treePath.index]
        hthDF=hthDF.loc[treePath.index]
        hthDF.columns=[i.split('.')[0].replace('X','',1) for i in hthDF.columns]
        commonTF=list(set(self.tfList).intersection(set(hthDF.columns)))
        hthDF=hthDF.loc[:,commonTF]
        extantControl.columns=[i.split('.')[0] for i in extantControl.columns]
        distanceMatrix.columns=distanceMatrix.index
        treePath.path=treePath.path.apply(lambda x:list(map(int,x.split(','))))
        root=treePath['path'][0][0]
        extantModel=pd.concat([hthDF.sum(axis=1),extantControl.sum(axis=1)],axis=1)
        extantModel.columns=['TF_OG','Random_OG']
        extantModel.loc[:,['log_TF_OG','log_Random_OG']]=extantModel.apply(log10).values
        extantModel.loc[:,phylumInfo.columns]=phylumInfo.loc[extantModel.index.values].values
        extantModel.loc[:,'node']=treePath.loc[extantModel.index.values,'node'].values
        extantModel['distanceFromRoot']=distanceMatrix.loc[extantModel.node.values,root].values
        extantModel=extantModel[extantModel.superkingdom=='Bacteria']
        for i in extantModel[extantModel.superkingdom!='Archaea'].index:
            _=[bacterial_node.append(j) for j in treePath.loc[i,'path'][1:-1] if j not in bacterial_node]
        return bacterial_node,extantModel,distanceMatrix,root
    
    def asrFilePrepartor(self,controlFile:str,hthFile:str):
        asrControl=self.reader(controlFile)
        asrHTH=self.reader(hthFile)

        asrControl.columns=[i.split('.')[0].split('_')[0].replace('X','',1) for i in asrControl.columns]
        asrHTH.columns=[i.split('.')[0].split('_')[0].replace('X','',1) for i in asrHTH.columns]
        commonTF=list(set(self.tfList).intersection(set(asrHTH.columns)))
        asrHTH=asrHTH.loc[:,commonTF]
        asrHTH,asrControl=asrHTH.loc[self.bacterial_node],asrControl.loc[self.bacterial_node]

        asrModel=pd.concat([asrHTH.sum(axis=1),asrControl.sum(axis=1)],axis=1)
        asrModel.columns=['TF_OG','Random_OG']
        asrModel.loc[:,['log_TF_OG','log_Random_OG',]]=asrModel.apply(log10).values
        asrModel['distanceFromRoot']=self.distanceMatrix.loc[asrModel.index,self.root]
        asrModel['node']=asrModel.index.astype(int)
        asrModel['NodeType']='Internal Node'
        return asrModel
    
    def modelTrainer(self):
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split

        model=LinearRegression()    
        x,y=self.extantDF.loc[:,'log_Random_OG'],self.extantDF.loc[:,'log_TF_OG']
        x_train,_,y_train,_=train_test_split(x,y,test_size=.9,random_state=2258)
        trainIndex=x_train.index
        model.fit(x_train.values.reshape(-1,1),y_train.values)
        self.extantDF['Train']=False
        self.extantDF.loc[trainIndex,'Train']=True
        self.extantDF['NodeType']='Extant'
        return model
    
    @staticmethod
    def reader(file:str):
        df=pd.read_csv(file,sep='\t',index_col=0)
        return df

    @staticmethod
    def tfListPreparotr(tfFile:str):
        tfList=[]
        with open(tfFile,'r') as f:
            count=False
            for i in f.readlines():
                if count:
                    if i.strip().split('\t')[-1]=='TF':
                        tfList.append(i.split('\t')[0].split('.')[0].split('_')[0].replace('X','',1))
                else:
                    count=True
        return tfList

    @staticmethod
    def predictorModel(model,df:pd.DataFrame):
        df['predict_log_TF']=model.predict(df.log_Random_OG.values.reshape(-1,1)) #type:ignore
        df['residual']=(df.log_TF_OG-df.predict_log_TF)
        return df

def __test__():
    extantControlFile='organismMatrixBin.16SrRNA_1.tsv'
    extantOGFile='organismMatrixBin.16SrRNA_1.tsv'
    phylumFile='phylumInfo.tsv'
    distanceFile='16SrRNA.pruned.tree_1.distanceMatrix'
    treePathFile='16SrRNA.pruned.tree_1.treePath'
    tfFile='Potential_TF_OG.tsv'
    asrControlFile='NodeAsrPresentAt75.tsv'
    asrOGFile='NodeAsrPresentAt75.tsv'

    lmmodel=LMModel(extantControlFile=extantControlFile,
    asrControlFile=asrControlFile,
    extantOGFile=extantOGFile,
    asrOGFile=asrOGFile,
    distanceFile=distanceFile,
    phylumFile=phylumFile,
    treePathFile=treePathFile,
    tfFile=tfFile)
    df=lmmodel.worker()
    print(df)
    return None

def main(configFile):
    from json import load
    from pprint import pprint
    with open(configFile,'r') as f:
        config=load(f)
    pprint(config)
    extantControlFile=config['extantControlFile']
    extantOGFile=config['extantOGFile']
    phylumFile=config['phylumFile']
    distanceFile=config['distanceFile']
    treePathFile=config['treePathFile']
    tfFile=config['tfFile']
    asrControlFile=config['asrControlFile']
    asrOGFile=config['asrOGFile']

    lmmodel=LMModel(extantControlFile=extantControlFile,
    asrControlFile=asrControlFile,
    extantOGFile=extantOGFile,
    asrOGFile=asrOGFile,
    distanceFile=distanceFile,
    phylumFile=phylumFile,
    treePathFile=treePathFile,
    tfFile=tfFile)
    df=lmmodel.worker()
    df.to_csv(config['output'],sep='\t')
    return None

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
