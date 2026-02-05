# ==============================================================================
# Project: Quantitative Investment Strategy Based on Shiller PE (CAPE) Ratio
# Author: Yu Cyuan (Ian) Huang
# Description: This script implements the core quantitative framework of my 
#              Master's Thesis, including CPI adjustment, CAPE calculation, 
#              regression analysis, and trading signal generation for ETF 0050/0051.
# ==============================================================================

# Load necessary libraries
library(tidyverse)
library(zoo)
library(TTR)

# ------------------------------------------------------------------------------
# 1. Data Preprocessing: CPI Inflation Adjustment & Earnings Calculation
# ------------------------------------------------------------------------------

# (1) Add CPI Base Year: Dynamically adjusted based on year intervals 
#     to ensure historical earnings comparability.
data <- data %>%
  mutate(
    CPI_Base_Year = case_when(
      Year >= 2023 ~ 2024,  
      Year >= 2021 ~ 2023,  
      Year >= 2019 ~ 2021,  
      Year >= 2017 ~ 2019,  
      Year >= 2015 ~ 2017,  
      Year >= 2013 ~ 2015,  
      Year >= 2011 ~ 2013,  
      Year >= 2009 ~ 2011,  
      Year >= 2007 ~ 2009,  
      Year >= 2005 ~ 2007,  
      Year >= 2003 ~ 2005,  
      Year >= 2001 ~ 2003,  
      Year >= 1999 ~ 2001,
      Year >= 1997 ~ 1999,
      TRUE ~ NA_real_        
    ),
    # Match CPI values for the corresponding base year
    CPI_Base = ifelse(!is.na(CPI_Base_Year), cpi_data$CPI[match(CPI_Base_Year, cpi_data$Year)], NA)
  )

# (2) Calculate Inflation-Adjusted EPS (Real EPS)
data <- data %>%
  mutate(EPS_Adjusted = EPS * (CPI_Base / CPI))

# (3) Data Aggregation: Calculate quarterly mean for EPS and Closing Price
data_quarterly <- data %>%
  group_by(Year, Quarter) %>%
  summarise(
    EPS_Quarterly = mean(EPS_Adjusted, na.rm = TRUE), 
    Closing_Price_Quarterly = mean(收盤價, na.rm = TRUE), # Keep column name if your raw data uses '收盤價'
    .groups = 'drop'
  )

# ------------------------------------------------------------------------------
# 2. Shiller PE (CAPE) Ratio & Moving Average (MA) Calculation
# ------------------------------------------------------------------------------

# (4) Calculate Quarterly CAPE Ratio (using 8-quarter/2-year rolling average EPS)
cape_results <- data_quarterly %>%
  arrange(Year, Quarter) %>%
  mutate(
    Two_Year_Avg_EPS = rollapply(EPS_Quarterly, width = 8, FUN = mean, align = "right", fill = NA),
    CAPE_Ratio = Closing_Price_Quarterly / Two_Year_Avg_EPS
  ) %>%
  filter(!is.na(Two_Year_Avg_EPS))

# (5) Calculate Technical Indicators: MA4, MA8, and MA12
cape_results <- cape_results %>%
  mutate(
    MA4 = SMA(CAPE_Ratio, n = 4),
    MA8 = SMA(CAPE_Ratio, n = 8), 
    MA12 = SMA(CAPE_Ratio, n = 12)  
  )

# ------------------------------------------------------------------------------
# 3. Statistical Validation: OLS Regression Analysis
# ------------------------------------------------------------------------------

# (6) Build Linear Regression Models: Validate MA indicators' explanatory power on price
model_ma4  <- lm(Closing_Price_Quarterly ~ MA4, data = cape_results)
model_ma8  <- lm(Closing_Price_Quarterly ~ MA8, data = cape_results)
model_ma12 <- lm(Closing_Price_Quarterly ~ MA12, data = cape_results)

# (7) Review Statistical Results (R-squared and Coefficient Significance)
summary(model_ma4)
summary(model_ma8)
summary(model_ma12)

# (8) Extract P-Values and Summarize in a Table
p_values <- tibble(
  Model = c("MA4", "MA8", "MA12"),
  P_Value = c(
    summary(model_ma4)$coefficients[2, 4],
    summary(model_ma8)$coefficients[2, 4],
    summary(model_ma12)$coefficients[2, 4]
  )
)
print("Statistical Significance (P-Values):")
print(p_values)

# ------------------------------------------------------------------------------
# 4. Trading Signal Generation
# ------------------------------------------------------------------------------

# (9) Calculate Signal Deviations (Based on thesis findings: MA8 for TAIEX, MA12 for TW50)
cape_results <- cape_results %>% 
  mutate( 
    Signal_Value_TAIEX = CAPE_Ratio - MA8, 
    Signal_Value_TW50 = CAPE_Ratio - MA12 
  )

# (10) Calculate 4-quarter Moving Average of Signal Values (Smoothing)
cape_results <- cape_results %>% 
  mutate( 
    Signal_MA_TAIEX = SMA(Signal_Value_TAIEX, n = 4),
    Signal_MA_TW50 = SMA(Signal_Value_TW50, n = 4) 
  )

# (11) Determine Entry/Exit Points (When signal crosses its moving average)
cape_results <- cape_results %>% 
  mutate( 
    Trading_Signal_TAIEX = Signal_Value_TAIEX - Signal_MA_TAIEX,
    Trading_Signal_TW50 = Signal_Value_TW50 - Signal_MA_TW50
  )

print("Quantitative Trading Signals Generated Successfully.")