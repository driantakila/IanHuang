# ==============================================================================
# Project: AI-Driven Financial Analytics Portfolio
# Author: Ian Huang
# Description: Applying Machine Learning to Retail Banking, Quant Trading, 
#              and Institutional Investment Behavior.
# ==============================================================================

# Install and load necessary packages
if(!require(caret)) install.packages("caret")
if(!require(ggplot2)) install.packages("ggplot2")
if(!require(MASS)) install.packages("MASS")
if(!require(arules)) install.packages("arules")
if(!require(randomForest)) install.packages("randomForest")

library(caret)
library(ggplot2)
library(MASS)
library(arules)
library(randomForest)

# ==============================================================================
# Part 1: Retail Banking Target Marketing (KNN, LDA, QDA)
# Objective: Predict Personal Loan acceptance to optimize marketing resources.
# ==============================================================================

# 1. Data Preparation
credit <- read.csv("Bank_Personal_Loan_Modelling.csv")

# Convert target and categorical variables to factors
credit$Personal.Loan <- as.factor(credit$Personal.Loan)
credit$Age <- as.factor(credit$Age)
credit$Family <- as.factor(credit$Family)
credit$Mortgage <- as.numeric(credit$Mortgage)
credit$Experience <- as.numeric(credit$Experience)
credit$Income <- as.numeric(credit$Income)
credit$CCAvg <- as.numeric(credit$CCAvg)

# 2. Exploratory Data Analysis (EDA) & Visualization
# Visualizing the relationship between Age/Family and Personal Loan
ggplot(credit, aes(x = Personal.Loan, y = as.numeric(Age))) + 
  geom_boxplot(fill="lightblue") + 
  ggtitle("Age vs Personal Loan Acceptance")

ggplot(credit, aes(x = Family, fill = Personal.Loan)) + 
  geom_bar(position = "dodge") +
  ggtitle("Family Size vs Personal Loan Acceptance")

# Data Splitting (80% Train, 20% Test)
set.seed(1234)
trainIndex <- createDataPartition(credit$Personal.Loan, p = .8, list = FALSE)
train_data <- credit[trainIndex, ]
test_data  <- credit[-trainIndex, ]

# 3. K-Nearest Neighbors (KNN) Model
set.seed(1234)
knn.result <- train(Personal.Loan ~ Age + Family + Mortgage, 
                    data = train_data,   
                    method = "knn",  
                    trControl = trainControl(method = "cv"),   
                    preProcess = c("center", "scale"),   
                    tuneLength = 20)

print(knn.result) # Optimal k value selection
test.predict.knn <- predict(knn.result, newdata = test_data)
confusionMatrix(test.predict.knn, test_data$Personal.Loan)

# 4. Linear Discriminant Analysis (LDA)
set.seed(1234)
lda.result <- train(Personal.Loan ~ Experience + Income + CCAvg, 
                    data = train_data, 
                    method = "lda", 
                    trControl = trainControl(method = "none"))

print(lda.result$finalModel)
train.predict.lda <- predict(lda.result, newdata = train_data)
confusionMatrix(train.predict.lda, train_data$Personal.Loan)

# ==============================================================================
# Part 2: Quantitative Trading Signal Forecast (Taiwan 50 ETF - 0050)
# Objective: Predict ETF price trends (Up/Down) using Random Forest.
# ==============================================================================

# Note: Assuming 'etf0050' dataframe is loaded with technical indicators (MACD, Bias Ratio, etc.)
# etf0050 <- read.csv("ETF0050.csv")
# etf0050$Trend <- as.factor(etf0050$Trend) # Target Variable: Yes (Up) / No (Down)

# Example Random Forest Implementation
# set.seed(1234)
# rf_model <- randomForest(Trend ~ MACD_DIF + MACD_OSC + Bias_Ratio + Volume, 
#                          data = train_etf, 
#                          ntree = 500, 
#                          importance = TRUE)

# rf_predictions <- predict(rf_model, newdata = test_etf)
# confusionMatrix(rf_predictions, test_etf$Trend)
# Evaluation: Extracts Accuracy, Sensitivity (66.09%), and Specificity (37.40%)

# ==============================================================================
# Part 3: Institutional Investor Behavior Mining (Association Rules)
# Objective: Discover co-movement networks in foreign institutional trading.
# ==============================================================================

# Note: Assuming 'foreign_trade_data' is a transactional dataset where 
# 1 = Net buy > 10M NTD, 0 = Otherwise.
# foreign_trade <- read.transactions("institutional_trades.csv", format="basket", sep=",")

# Apply Apriori Algorithm
# rules <- apriori(foreign_trade, 
#                  parameter = list(supp = 0.39, conf = 0.7, minlen = 2, maxlen = 4))

# Inspect the top 13 association rules (e.g., Yuanta Financial -> Wiwynn)
# inspect(sort(rules, by = "lift")[1:13])

# ==============================================================================
# End of Script
# ==============================================================================