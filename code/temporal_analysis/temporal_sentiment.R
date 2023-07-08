library(stringr)
library(lubridate)
library(dplyr)
library(ggplot2)
library(ggsci)
library(zoo)
library(plotrix)

analyse_sentiment <- function(datafile, country.choice, ndays, num.bootstraps, outpref)
{
  
  df <- read.table(datafile, sep = ",", comment.char = "", quote = "", header = 1)
  
  # parse location
  Location <- as.data.frame(str_split_fixed(df$Location, ":", 3))
  colnames(Location) <- c("Country", "Region", "City")
  df <- cbind(df, Location)
  
  # parse data/time
  df$Date_time <- parse_date_time(df$Date_time, "Ymd HMS")
  df$Date <- as.Date(df$Date_time)
  df$Time.hour <- hour(df$Date_time)
  df$Time.minute <- minute(df$Date_time)
  
  count.df <- df %>%
    group_by(Country, Date) %>%
    summarise(Negative = sum(Sentiment == "negative"), Positive = sum(Sentiment == "positive"), Neutral = sum(Sentiment == "neutral"))
  
  count.df$Total <- count.df$Negative + count.df$Positive + count.df$Neutral
  count.df$Prop.negative <- count.df$Negative / count.df$Total
  
  
  subset.df <- subset(count.df, Country == country.choice)
  if (nrow(subset.df) == 0)
  {
    country.choice = "Global"
    df$Country <- country.choice
    
    subset.df <- df %>%
      group_by(Date) %>%
      summarise(Country = "Global", Negative = sum(Sentiment == "negative"), Positive = sum(Sentiment == "positive"), Neutral = sum(Sentiment == "neutral"))
    
    subset.df$Total <- subset.df$Negative + subset.df$Positive + subset.df$Neutral
    subset.df$Prop.negative <- subset.df$Negative / subset.df$Total
  }
  
  all_dates = tidyr::full_seq(df$Date,1)
  subset.df2 <- expand.grid(Country=country.choice, Date=all_dates, Negative=0, Positive=0, Neutral=0, Total=0, Prop.negative=0)
  
  subset.df = rbind(subset.df, subset.df2) %>%
    group_by(Country, Date) %>%
    summarize(Negative=sum(Negative), Positive=sum(Positive), Neutral=sum(Neutral), Total=sum(Total), Prop.negative=sum(Prop.negative)) %>%
    ungroup()
  
  # generate bootstraps
  bootstrap.df <- t(apply(subset.df, 1, function(x) rbinom(num.bootstraps, as.numeric(x[6]), as.numeric(x[7]))))
  
  subset.df$boostrap.avg <- rowMeans(bootstrap.df)
  subset.df$boostrap.se <- apply(bootstrap.df, 1, sd, na.rm=TRUE) / sqrt(ncol(bootstrap.df))
  
  # save csv
  write.csv(subset.df, paste(outpref, "_time_series.csv", sep = ""), row.names = FALSE)
  

  rolling.bs.avg <- rep(NA, length(all_dates))
  rolling.bs.se <- rep(NA, length(all_dates))
  
  cols <- ndays:length(all_dates)
  for(i in cols) {
    obs.mat <- bootstrap.df[(i-(ndays-1)):(i),]
    rolling.bs.avg[i] <- mean(obs.mat)
    rolling.bs.se[i] <- sd(obs.mat) / sqrt(length(obs.mat))
  }
  
  subset.df <- transform(subset.df, avg.neg = rollmeanr(Negative, ndays, fill = NA))
  subset.df <- transform(subset.df, avg.neg.prop = rollmeanr(Prop.negative, ndays, fill = NA))
  subset.df$avg.neg.bs <- rolling.bs.avg
  subset.df$avg.neg.bs.se <- rolling.bs.se
  #subset.df <- transform(subset.df, avg.neg.bs = rollmeanr(boostrap.avg, ndays, fill = NA))
  #subset.df <- transform(subset.df, avg.neg.bs.se = rollmeanr(boostrap.se, ndays, fill = NA))
  
  p <- ggplot(subset.df, aes(x = Date, y = avg.neg)) + geom_ribbon(aes(ymin=avg.neg.bs-(1.96*avg.neg.bs.se), ymax=avg.neg.bs+(1.96*avg.neg.bs.se), fill = "#E74C3C")) + geom_path(linewidth=0.7) + theme_light() + theme(axis.text.x = element_text(size = 14), axis.text.y = element_text(size = 12), axis.title=element_text(size=16,face="bold"), strip.text.x = element_text(size = 11), legend.title=element_text(size=14,face="bold"), legend.text=element_text(size=12), legend.position = "none") + ylab(paste("No. Negative Tweets (", ndays, "-day rolling average)", sep = "")) + scale_fill_npg()
  p
  ggsave(file=paste(outpref, "_rolling_average.svg", sep = ""), plot=p, height = 8, width = 15)
}


#initial setup
datafile = "vax_tweets_parsed.csv"
ndays <- 30
num.bootstraps <- 100

#US analysis
country.choice <- "United States of America"
outpref <- "US_analysis"
analyse_sentiment(datafile, country.choice, ndays, num.bootstraps, outpref)

#Uk analysis
country.choice <- "United Kingdom"
outpref <- "UK_analysis"
analyse_sentiment(datafile, country.choice, ndays, num.bootstraps, outpref)

# India analysis
country.choice <- "India"
outpref <- "India_analysis"
analyse_sentiment(datafile, country.choice, ndays, num.bootstraps, outpref)

# Global analysis
country.choice <- "Global"
outpref <- "Global_analysis"
analyse_sentiment(datafile, country.choice, ndays, num.bootstraps, outpref)

