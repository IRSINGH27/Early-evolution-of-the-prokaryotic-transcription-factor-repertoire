library(optparse)

getPapa<-function(tree,node,curr=NULL){
  if(is.null(curr)) curr<-vector()
    daughters<-tree$edge[which(tree$edge[,2]==node),1]
    curr<-c(curr,daughters)
    x<-length(tree$tip)+1
    w<-which(daughters>=x)
    if(length(w)>0) for(i in 1:length(w))
      curr<-getPapa(tree,daughters[w[i]],curr)
    return(curr)
}

worker <-function(treeFileName,pmatrixOutput,dmatrixOutput,root){
    tree<-treeio::read.tree(treeFileName)
    tree <- ape::multi2di(tree)
    if (root==0){
      tree <- phytools::midpoint.root(tree)
      tree$edge.length[tree$edge.length == 0] <- 1e-5
      tree$node.label <- NULL
    }
    tree$node.label<-seq(length(tree$tip.label)+1,length(tree$tip.label)+1+tree$Nnode)
    print("treeRead")
    df<-castor::get_all_pairwise_distances(tree)
    write.table(df,dmatrixOutput,sep='\t',quote = F)
    print("path")
    pathDF<-data.frame(row.names = tree$tip.label)
    pathDF$node<-treeio::nodeid(tree,row.names(pathDF))
    pathDF$PathID<-unlist(lapply(pathDF$node,FUN = function(x){paste('Path_',x,collapse = '')}))
    pathDF$path<-unlist(lapply(pathDF$node,FUN = function(x){paste(append(unlist(rlist::list.reverse(getPapa(tree,x))),x),collapse = ',')}))
    pathDF<-pathDF[order(pathDF$node),]

    write.table(pathDF,pmatrixOutput,sep='\t',quote = F)
    }
options<-list(
    make_option(c("--treeFileName"),type="character",help="Input Tree File"),
    make_option(c("--dmatrixOutput"),type="character",help="Distance Matrix"),
    make_option(c("--pmatrixOutput"),type="character",help="path Matrix Table"),
    make_option(c("--root"),help="rooted or not")
)

opt_parser <- OptionParser(option_list = options)
arguments <- parse_args(opt_parser)


treeFileName<-arguments$treeFileName
dmatrixOutput<-arguments$dmatrixOutput
pmatrixOutput<-arguments$pmatrixOutput
root<-arguments$root

worker(treeFileName = treeFileName,pmatrixOutput = pmatrixOutput,dmatrixOutput = dmatrixOutput,root = root)

# treeFileName<-'/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/treeMaking/16s_GTDB/16SrRNA_tree.pruned.besttree'
# dmatrixOutput<-'/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/treeMaking/16s_GTDB/distanceMatrix.tsv'
# pmatrixOutput<-'/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/treeMaking/16s_GTDB/treePath.tsv'
