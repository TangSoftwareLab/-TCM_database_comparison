library(pheatmap)
library(ComplexHeatmap)
library("RColorBrewer")
herb_info = read.csv('../result/herb_info.csv',
                      row.names = 1,
                      encoding="UTF-8", 
                      stringsAsFactors=FALSE)

formulae_info = read.csv('../result/formulae.csv',
                     row.names = 1,
                     encoding="UTF-8", 
                     stringsAsFactors=FALSE)
formulae_info_binary = formulae_info[c("Traditional.function",
                                       "Indication", 
                                       "Function.class","Usage")]
fomulae_number <- formulae_info$Number
colfunc <- colorRampPalette(c("white", "red"))

p_1 = pheatmap(
  herb_info, 
         color = colfunc(2),
         fontsize = 15,
  cluster_rows = FALSE,
  show_row_dend = FALSE,
  border = TRUE)
p_1
p_2 = pheatmap(formulae_info_binary , 
               color = colfunc(2),
               fontsize = 15,
               cluster_rows = FALSE,
               show_row_dend = FALSE,
               border = TRUE)

p_3 = rowAnnotation(formulae = anno_barplot(fomulae_number),
                    annotation_name_side = "bottom", 
                    width = unit(4, "cm"))

p_1 + p_3 + p_2  
