library(optparse)

checker<-function(file,output){
    load(file)
    if (("model.ard" %in% ls()) & ("model.er" %in% ls())){

        if ((typeof(model.ard)==typeof(list())) & ((typeof(model.er)==typeof(list())))){
            if (model.ard$loglik>model.er$loglik){
                tmatrix<-phytools::as.Qmatrix(model.ard)
                likmatrix<-model.ard$lik.anc
                model<-'ard'
                
            } else{
                tmatrix<-phytools::as.Qmatrix(model.er)
                likmatrix<-model.er$lik.anc
                model<-'er'

            }
        } else{
            if (typeof(model.ard)==typeof(list())) {
                tmatrix<-phytools::as.Qmatrix(model.ard)
                likmatrix<-model.ard$lik.anc
                model<-'ard'

            } else{
                if (typeof(model.er)==typeof(list())){
                tmatrix<-phytools::as.Qmatrix(model.er)
                likmatrix<-model.er$lik.anc
                model<-'er'
                }
            }
        }
    } else {
        if ("model.ard" %in% ls()) {
        tmatrix<-phytools::as.Qmatrix(model.ard)
        likmatrix<-model.ard$lik.anc
        model<-'ard'
        } else {
            tmatrix<-phytools::as.Qmatrix(model.er)
            likmatrix<-model.er$lik.anc
            model<-'er'
        }
    }
    fname<-basename(file)
    fname<-unlist(strsplit(fname,'\\.'))[1]
    write.table(tmatrix,file=paste(output,fname,'_transtion.tsv',sep=''),sep='\t',quote = F)
    write.table(likmatrix,file=paste(output,fname,'_likanc.tsv',sep=''),sep='\t',quote = F)
    # return(data.frame(model = model, file = fname))
}


options<-list(
    make_option(c("--input"),type="character",help="Input File"),
    make_option(c("--outputFolder"),type="character",help="Output Folder")
)

opt_parser <- OptionParser(option_list = options)
arguments <- parse_args(opt_parser)

file<-arguments$input
output<-arguments$output

checker(file,output)