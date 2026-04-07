library(doParallel)
library(ape)
library(phytools)
library(optparse)

simulationFunction<-function(cogFile,treeFile,outputFile,ncores,root){
    tree <- read.tree(treeFile)
    if (root=='T'){
        tree <- phytools::midpoint.root(tree)
        tree <- ape::multi2di(tree)
    } 
    tree$edge.length[tree$edge.length == 0] <- 1e-5
    tree$node.label <- seq(length(tree$tip.label)+1,length(tree$tip.label)+tree$Nnode)
    print('treeRead')
    Qmatrix<-as.matrix(read.csv(cogFile,sep='\t',row.names=1))
    colnames(Qmatrix)<-NULL
    row.names(Qmatrix)<-NULL

# paral start
    cl <- makeCluster(ncores)
    on.exit(stopCluster(cl),add=T)
    registerDoParallel(cl)
    finalDF<-foreach(i=seq(1,100),.packages=c('ape'),.combine=cbind) %dopar% {
        result<-rTraitDisc(tree,model=Qmatrix,state=c(0,1),ancestor=T)
        df<-data.frame(result)
        colnames(df)<-paste0('simu_',as.character(i),collapse='')
        return(df)
    }
    write.table(finalDF,outputFile,sep='\t',quote=F)
}

options<-list(
    make_option(c("--cogFile"),type="character",help="Q for ASR"),
    make_option(c("--treeFile"),type="character",help="treeFile for ASR"),
    make_option(c("--outputFile"),type="character",help="simu result"),
    make_option(c("--root"),type="character",help="Rooted or not"),
    make_option(c("--ncores"),type="numeric",help="cores ",default=1)
)

opt_parser <- OptionParser(option_list = options)
arguments <- parse_args(opt_parser)

cogFile<-arguments$cogFile
treeFile<-arguments$treeFile
outputFile<-arguments$outputFile
ncores<-arguments$ncores
root<-arguments$root

simulationFunction(cogFile,treeFile,outputFile,ncores,root)