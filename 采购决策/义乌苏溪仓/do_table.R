library(readxl)
	
	p <- scan("p.txt")
	ti1 <- read_excel("ti1.xls")
	ti2 <- read_excel("ti2.xls")
	ti3 <- read_excel("../淘汰商品列表.xls")

	vendor <- read.table("../供应商列表.csv",header=TRUE,sep=",")

	#/*强制类型转换，保证数据格式正确*/
	
	ti1$商品编码 <- as.character(ti1$商品编码)
	ti1$规格编码 <- as.character(ti1$规格编码)
	ti1$销售数量 <- as.numeric(ti1$销售数量)
	ti1$期末库存数量 <- as.numeric(ti1$期末库存数量)
	
	ti2$"商品规格编码" <- as.character(ti2$"商品规格编码")

	ti3$淘汰商品 <- as.character(ti3$淘汰商品)
	
	vendor$商品编码 <- as.character(vendor$商品编码)
	
	#/*数据清洗，去掉不需要的制表符和空格*/
	ti1$商品编码 <- gsub("\t","",ti1$商品编码)
	ti1$商品编码 <- gsub(" ","",ti1$商品编码)

	ti1$规格编码 <- gsub("\t","",ti1$规格编码)
	ti1$规格编码 <- gsub(" ","",ti1$规格编码)


	####################生成to1#####################

	#/*从ti1表中取出符合预定条件的表项和列*/
	t1 <- ti1[c("商品编码","商品名称","规格编码","规格名称","销售数量","期末库存数量")]
	to1 <- subset(t1, p*销售数量 >= 期末库存数量)

	#/*相同商品编码的销售数量叠加求和*/
	a <- to1[c("商品编码","销售数量","期末库存数量")]
	b <- aggregate(a[,c(2,3)],by=list(商品编码=a$商品编码),FUN=sum)

	#/*上面求和过程生成的表与原来的表合并*/
	x <- b$销售数量[match(to1$商品编码, b$商品编码)]
	to1 <- cbind(to1,商品总销售数量=x)

	#/*合并后的表按照各商品编码的总销量进行降序排序*/
	to1 <- to1[order(-to1$商品总销售数量,to1$商品编码),]


	####################生成to2#####################

	#/*从to1中剔除ti2（采购订单表）中存在的规格编码*/
	to2 <- subset(to1,!(to1$规格编码 %in% ti2$"商品规格编码"))

	#/*继续剔除ti3（淘汰商品列表）中存在的商品编码和规格编码*/
	to2 <- subset(to2,!(to2$商品编码 %in% ti3$淘汰商品))
	to2 <- subset(to2,!(to2$规格编码 %in% ti3$淘汰商品))


	####################生成to3#####################
	x <- as.vector(vendor$供应商名称[match(to2$商品编码, vendor$商品编码)])
	for(i in 1:length(x)) if (is.na(x[i])) x[i]<-paste("无供应商信息，商品编码：",to2$商品编码[i])

	y <- cbind(to2,供应商=as.vector(x))

	u <- aggregate(y[,"商品总销售数量"],by=list(供应商=y$供应商),FUN=max)

	v <- u$x[match(y$供应商, u$供应商)]
	y <- cbind(y,供应商最大单品销量=v)
	y <- y[order(-y$供应商最大单品销量,y$供应商,-y$商品总销售数量,y$商品编码),]
	to3 <- y

	####################输出结果#####################y

	#/*to1不同商品编码组中间加入分隔行*/
	k <- NULL
	for(i in 2:length(to1$商品编码))  if(to1$商品编码[i] != to1$商品编码[i-1]) k <- c(k,i-1)
	for(i in 1:length(k)) {len<-length(to1$商品编码); to1 <- rbind(to1[1:(k[i]+i-1),],"--------",to1[(k[i]+i):len,])}
	write.table(to1,"to1.csv",sep=",",row.names=FALSE)

	#/*to2不同商品编码组中间加入分隔行*/
	k <- NULL
	for(i in 2:length(to2$商品编码))  if(to2$商品编码[i] != to2$商品编码[i-1]) k <- c(k,i-1)
	for(i in 1:length(k)) {len<-length(to2$商品编码); to2 <- rbind(to2[1:(k[i]+i-1),],"--------",to2[(k[i]+i):len,])}
	write.table(to2,"to2.csv",sep=",",row.names=FALSE)


	#/*to3不同供应商组、不同商品编码组中间加入分隔行*/
	k <- NULL
	k[1]<-3
	for(i in 1:(length(to3$商品编码)-1)) 
	{ 
	k[i+1] <- 0
	if(to3$商品编码[i] != to3$商品编码[i+1]) k[i+1] <- 1
	if(to3$供应商[i] != to3$供应商[i+1]) k[i+1] <- 3
	}

	to3$供应商 <- as.vector(to3$供应商)

	heavy_gap <- "==========="
	heavy_gap[1:ncol(to3)] <- heavy_gap
	heavy_gap[2] <- paste(rep('=',1.5*max(nchar(to3[,2]))),collapse="")

	light_gap <- "-----------"
	light_gap[1:ncol(to3)] <- light_gap
	light_gap[2] <- paste(rep('-',1.5*max(nchar(to3[,2]))),collapse="")

	#/*插入首行*/

	to3 <- rbind(heavy_gap,to3)
	gap <- heavy_gap
	gap[1:ncol(to3)] <- "         "
	gap[1] <- "==         "
	gap[2] <- paste(to3$供应商[2],"    旺旺号：", vendor$供应商旺旺号[match(to3$供应商[2],vendor$供应商名称)])
	gap[9] <- "         =="
	to3 <- rbind(gap,to3)
	to3 <- rbind(heavy_gap,to3)

	#/*j代表插入的分隔行的行数 */
	j <- 3

	for(i in 2:length(k)) 
	{
	if (k[i] != 0)
		{
			if (k[i] == 1) 
				to3 <- rbind(to3[1:(i+j-1),],light_gap,to3[(i+j):nrow(to3),])
					
			else 
				{
				
				to3 <- rbind(to3[1:(i+j-1),],heavy_gap,to3[(i+j):nrow(to3),])
				
				gap[1:ncol(to3)] <- "         "
				gap[1] <- "==         "
				gap[2] <- paste(to3$供应商[i+j+1],"    旺旺号：", vendor$供应商旺旺号[match(to3$供应商[i+j+1],vendor$供应商名称)])
				gap[9] <- "         =="
				to3 <- rbind(to3[1:(i+j-1),],gap,to3[(i+j):nrow(to3),])
				
				to3 <- rbind(to3[1:(i+j-1),],heavy_gap,to3[(i+j):nrow(to3),])
				}
			j <- j+k[i]
		}

	}

	write.table(to3,"to3.csv",sep=",",row.names=FALSE)





