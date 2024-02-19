library(car)
library(tidyverse)
library(mgcv)
library('e1071')
library(caret)
library(nycflights13)
library(ggplot2)
library(pls)
library(reshape2)
library(ggplot2)
library(lattice)
library (VennDiagram)
library(UpSetR)
library(reshape2)
library(corrplot)
library(RColorBrewer)
library(gridExtra)
library(gridGraphics)
library(pheatmap)

windowsFonts(
  A=windowsFont("Arial Black"),
  B=windowsFont("Bookman Old Style"),
  C=windowsFont("Comic Sans MS"),
  D=windowsFont("Symbol")
)


col1 <-rainbow(50, s = 1, v = 1, start = 0, end = 1, alpha = 0.7)



# 1. herb overlap 
herbs <- read.csv('../result/table/herb_overlap.csv',
                  encoding="UTF-8", 
                  stringsAsFactors=FALSE, 
                  row.names = 1)
names(herbs) <- gsub("\\.", "-", names(herbs))
upset(herbs, sets = c('ETCM',
                      'SymMap',
                      'HERB',
                      'TCM-ID',
                      'TCM-Mesh',
                      'TCMID',
                      'TCMIO',
                      'TCMSP',
                      'TM-MC' ),
      nintersects = 30,
      order.by = "freq", 
      empty.intersections = "on",
      show.numbers='yes',
      color.pal = 1,
      sets.bar.color=c("maroon",
                       "orange",
                       "blue",
                       "darkgreen",
                       'red',
                       'grey',
                       'darkgreen',
                       "gold",
                       "purple" ),
      mainbar.y.label = '',
      sets.x.label = 'Number',
      point.size = 5.5,
      text.scale = 1.7)


grid.edit('arrange', name='over_compound')
herb_upset <- grid.grab()


# 2. read ingredients
ingredient = read.csv('../result/table/ingredient_overlap.csv',
                      row.names = 1,
                      encoding="UTF-8", 
                      stringsAsFactors=FALSE)

names(ingredient) <- gsub("\\.", "-", names(ingredient))

upset(ingredient, sets = c( 'ETCM',
                            'SymMap',
                            'HERB',
                            'TCM-ID',
                            'TCM-Mesh',
                            'TCMID',
                            'TCMSP',
                            'TM-MC' ),
      nintersects = 30,
      order.by = "freq", 
      empty.intersections = "on",
      show.numbers='yes',
      color.pal = 1,
      sets.bar.color=c("maroon",
                       "orange",
                       "blue",
                       "darkgreen",
                       'red',
                       'darkgreen',
                       "gold",
                       "purple"),
      mainbar.y.label = '',
      sets.x.label = 'Number',
      point.size = 5.5,
      text.scale = 1.7)
grid.edit('arrange', name='model')
ingredient_upset <- grid.grab()


##correlation of Herb and  ingredients
cor_jacard_mean <- as.matrix(read.csv('../result/table/cor_jacard_mean.csv',
                  encoding="UTF-8", 
                  stringsAsFactors=FALSE,
                  row.names = 1))

colnames(cor_jacard_mean) <- gsub("\\.", "-", colnames(cor_jacard_mean))
row.names(cor_jacard_mean) <- gsub("\\.", "-", row.names(cor_jacard_mean))


cor_rate_mean <- as.matrix(read.csv('../result/table/cor_rate_mean.csv',
                                encoding="UTF-8", 
                                stringsAsFactors=FALSE,
                          row.names = 1))
colnames(cor_rate_mean) <- gsub("\\.", "-", colnames(cor_rate_mean))
row.names(cor_rate_mean) <- gsub("\\.", "-",row.names(cor_rate_mean))


cor_overlap_mean <- as.matrix(read.csv('../result/table/cor_overlap_mean.csv',
                             encoding="UTF-8", 
                             stringsAsFactors=FALSE,
                             row.names = 1))
colnames(cor_overlap_mean) <- gsub("\\.", "-", colnames(cor_overlap_mean))
row.names(cor_overlap_mean) <- gsub("\\.", "-", row.names(cor_overlap_mean))

cor_overlap_herb <- as.matrix(read.csv('../result/table/cor_overlap_herb.csv',
                             encoding="UTF-8", 
                             stringsAsFactors=FALSE,
                             row.names = 1))
colnames(cor_overlap_herb) <- gsub("\\.", "-", colnames(cor_overlap_herb))
row.names(cor_overlap_herb) <- gsub("\\.", "-", row.names(cor_overlap_herb))

# corrplot cor_jacard_mean
corrplot::corrplot(cor_jacard_mean, order = "alphabet", type = "upper",tl.pos = "d",
                   tl.col='black',col=col1, cl.pos= 'n',mar = c(0, 0, 0, 0)) 

corrplot::corrplot(cor_jacard_mean, add = TRUE, type = "lower", method = "number",
                   col='grey44', order = "alphabet",
                   diag = FALSE, tl.pos = "n", cl.pos = "n",mar = c(0, 0, 0, 0),bg = NULL )
grid.echo()
cor_jacard_mean_model <- grid.grab()


# corrplot cor_rate_mean
corrplot::corrplot(cor_rate_mean, order = "alphabet", type = "upper",tl.pos = "d",
                   tl.col='black',col=col1, cl.pos= 'n',mar = c(0, 0, 0, 0)) 

corrplot::corrplot(cor_rate_mean, add = TRUE, type = "lower", method = "number",col='grey44', order = "alphabet",
                   diag = FALSE, tl.pos = "n", cl.pos = "n",mar = c(0, 0, 0, 0),bg = NULL )
grid.echo()
cor_rate_mean_model <- grid.grab()


# matrix: overlap_mean 
pheatmap(cor_overlap_mean, 
         display_numbers = T,
         fontsize = 15)
grid.echo()
cor_overlap_mean_model <- grid.grab()


# matrix: overlap_herb

cor_overlap_herb <- round(cor_overlap_herb,0)
pheatmap(cor_overlap_herb,
         display_numbers = T,
         fontsize = 15)
grid.echo()
cor_overlap_herb_model <- grid.grab()


lay_2 <- rbind(c(1,2),
               c(3,4),
               c(5,6))


overlap_2= grid.arrange(grobs = list(herb_upset, 
                                     ingredient_upset,
                                     cor_jacard_mean_model,
                                     cor_rate_mean_model,
                                     cor_overlap_mean_model,
                                     cor_overlap_herb_model),
                        nrow =3, 
                        ncol=2,
                        clip = "on",
                        respect = FALSE,
                        layout_matrix = lay_2)


ggsave("../result/figure/correlation_R.pdf",overlap_2,width = 18,height= 18)
dev.off()
