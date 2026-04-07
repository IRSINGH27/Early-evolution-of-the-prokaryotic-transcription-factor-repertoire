library(optparse)

pruner<-function(treeFile,dfFile,outputDir,HTH){
    tree<-treeio::read.tree(treeFile)
    df<-read.csv(dfFile,sep='\t',row.names=1)
    commonOrganism<-intersect(tree$tip.label,row.names(df))
    df<-df[commonOrganism,]
    useCol<-colSums(df)
    useCol<-useCol[useCol!=0]
    df<-df[,names(useCol)]
    tree<-ape::keep.tip(tree,commonOrganism)
    tempName<-stringr::str_replace_all(basename(dfFile),'tsv',stringr::str_replace_all(basename(treeFile), '.tree', ''))
    tempName<-paste(tempName,'.tsv',sep='')
    if (HTH=='T'){
        dfName <- file.path(outputDir,'HTH', tempName)
    }
    if (HTH=='F'){
        dfName <- file.path(outputDir,'ZnBR', tempName)
    }
    if (HTH=='N'){
        dfName <- file.path(outputDir, tempName)
    }
    treeName <- file.path(outputDir, stringr::str_replace(basename(treeFile), '.tree', '.pruned.tree'))
    write.table(df,dfName,sep='\t',quote=F)
    treeio::write.tree(tree,treeName)
}

options<-list(
    make_option(c("--dataframe"),type="character",help="DataFrameFile"),
    make_option(c("--treeFile"),type="character",help="treeFile"),
    make_option(c("--outputDir"),type="character",help="outputDir"),
    make_option(c("--HTH"),type="character",help="outputDir")
)


opt_parser <- OptionParser(option_list = options)
arguments <- parse_args(opt_parser)

dataFrame=arguments$dataframe
treeFile=arguments$treeFile
outputDir=arguments$outputDir
HTH=arguments$HTH
pruner(treeFile=treeFile,dfFile=dataFrame,outputDir=outputDir,HTH=HTH)