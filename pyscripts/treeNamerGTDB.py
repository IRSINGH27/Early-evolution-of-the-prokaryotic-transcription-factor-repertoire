def main(treeFile:str,dfFile:str,output:str):
    from pandas import read_csv
    from Bio import Phylo
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
    Phylo.write(tree,f'{output}/ar53_2_withNameCorrected.tree','newick')

if __name__=='__main__':
    treeFile='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/treeMaking/GTDBPrune/arch/ar53.tree'
    dfFile='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/WoL_ZnBR_Organism_index.tsv'
    output='/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/finalTree/GTDBTree/arch/'
    main(treeFile,dfFile,output)