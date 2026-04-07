#!/home/aswin/irsingh/softwares/miniconda3/envs/codingEnv/bin/Rscript
library(doParallel)
library(ape)
library(phytools)
library(optparse)

asr <- function(dataFrame, treeFile, sep, output,root,ncores) {
    # Read data
    if (sep == 'c') {
        df <- read.csv(dataFrame, row.names = 1, sep = ',')
    } else {
        df <- read.csv(dataFrame, row.names = 1, sep = '\t')
    }
    print('dataFrameRead')

    # Read and preprocess tree
    tree <- read.tree(treeFile)
    if (root==0){
        tree <- phytools::midpoint.root(tree)
        tree <- multi2di(tree)
    } 
    tree$edge.length[tree$edge.length == 0] <- 1e-5
    tree$node.label <- NULL
    print('treeRead')
    df<-df[tree$tip.label,]
    useCol<-colSums(df)
    useCol<-useCol[useCol!=0]
    df<-df[,names(useCol)]
    # write.table(df,)
    # Parallel processing
    cl <- makeCluster(ncores)
    registerDoParallel(cl)
    colNames <- colnames(df)
    print('parel')
    print(head(df[,seq(1,5)]))
    print(dim(df))
    print(tree)
    foreach(i = colNames, .packages = c('ape', 'phytools')) %dopar% {
        cat("Processing column:", i, "\n")
        vector<-df[[i]]
        names(vector)<-row.names(df)
        tryCatch({
        print(paste('start',i,sep=' ',collapse = ' '))

        model.er <- ace(vector, phy = tree, type = 'discrete', marginal = TRUE, model = "ER")
        print(paste('er',i,sep=' ',collapse = ' '))
        model.ard <- ace(vector, phy = tree, type = 'discrete', marginal = TRUE, model = "ARD")
        print(paste('AR',i,sep=' ',collapse = ' '))

        imageName <- paste(output, i, 'asr', sep = '_')
        imageName <- paste(imageName, 'RData', sep = '.')
        save(model.er,model.ard,file = imageName)
        }, error=function(e){
            tryCatch({
                print('er1')
            model.er <- ace(vector, phy = tree, type = 'discrete', marginal = TRUE, model = "ER");
            imageName <- paste(output, i, 'asr', sep = '_');
            imageName <- paste(imageName, 'RData', sep = '.');
            save(model.er,file = imageName)
            }, error=function(e){
                print('er2')
                model.ard <- ace(vector, phy = tree, type = 'discrete', marginal = TRUE, model = "ARD")
                imageName <- paste(output, i, 'asr', sep = '_')
                imageName <- paste(imageName, 'RData', sep = '.')
                save(model.ard,file = imageName)
                })
                }
            )
            }
    on.exit(stopCluster(cl))
        }


options<-list(
    make_option(c("--dataFrame"),type="character",help="DataFrameFile for ASR"),
    make_option(c("--sep"),type="character",help="sep for DataFrame file for ASR"),
    make_option(c("--treeFile"),type="character",help="treeFile for ASR"),
    make_option(c("--output"),type="character",help="output dir for ASR"),
    make_option(c("--root"),type="numeric",,help="root tree or not ",default=0),
    make_option(c("--ncores"),type="numeric",,help="root tree or not ",default=1)
)

opt_parser <- OptionParser(option_list = options)
arguments <- parse_args(opt_parser)

dataFrame=arguments$dataFrame
treeFile=arguments$treeFile
output=arguments$output
sep=arguments$sep
ncores=arguments$ncores
root=arguments$root

# dataFrame="/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/HTH/Results/organismMatrix/hmmscanEG/binaryCount/eggNOG_hmmscan_HTH_binary.tsv"

# treeFile="/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/Results/treeMaking/16s_GTDB/16SrRNA_tree.pruned.besttree"

# output="/data/irsingh/Zinc_Work/WoL_reset_18Nov2025/HTH/Results/Ancestral_State_Reconstruction/16S_rRNA/asrFiles/"

# sep="t"

asr(dataFrame = dataFrame, treeFile = treeFile, sep=sep,root=root, output = output,ncores=ncores)