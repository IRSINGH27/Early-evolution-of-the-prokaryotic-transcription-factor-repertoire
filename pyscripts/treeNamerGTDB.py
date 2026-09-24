def main(configFile:str):
    from pandas import read_csv
    from Bio import Phylo
    from json import load
    with open(configFile,'r') as f:
        config=load(f)
    treeFile=config['treeFile']
    dfFile=config['dfFile']
    output=config['output']
    tree=Phylo.read(treeFile,'newick')
    df=read_csv(dfFile,sep='\t',index_col=0)
    df.index=df.assembly_accession.apply(lambda x:x.split('.')[0]).values
    f=open(f'{output}/KeepTip.txt','w')
    for i in tree.get_terminals():
        name=i.name
        if name in df.gtdb_id.to_list():
            print(1)
            val=df.loc[df.gtdb_id==name,'assembly_accession'].values[0].split('.')[0]
            print(val)
            i.name=val
            f.write(f'{val}\n')
        else:
            pass
    f.close()
    Phylo.write(tree,f'{output}','newick')

if __name__=='__main__':
    from argparse import ArgumentParser
    program=ArgumentParser(prog='Entro Calculator')
    program.add_argument('config',type=str)
    args=program.parse_args()
    main(args.config)
