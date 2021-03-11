# The task here is to construct two graphs (heatplot on US map) based on the adverse effects reported in US after COVID-19 vaccination

# The two figures show
# (i) The number of adverse effects (raw counts) across all states in US
# (ii) The number of adverse effects corrected for the number of senior citizens in all states

# The number of adverse effects were collected from VAERS website (https://vaers.hhs.gov/)

# The number of senior citizens for all states was collected as per record of 2019 in Statistica 
# The link is here: https://www.statista.com/statistics/736211/senior-population-of-the-us-by-state/


# For the first graph (raw count)

library(usmap)
library(scales)
library(ggplot2)
library(tidyverse)

a <- read.table(file = "us_raw_counts.txt", header = TRUE)



dddd <- plot_usmap(data = a, values = "Adverse_effects", color = "red", labels = T) + scale_fill_continuous(low = "white", high = "Red", name = "Adverse side effects", label = scales::comma) + theme(panel.background = element_rect(colour = "black")) + labs(title = "Distribution of COVID-19 vaccination adverse effects in US", face = "bold")
dddd + theme(text = element_text(size = 15))

# For the second graph (normalized to senior citizens)

a <- read.table(file = "us_senior_new.txt", header = T)

aa <- plot_usmap(data = a, values = "Effects_normalized_SC", color = "firebrick4", labels = T) + scale_fill_continuous(low = "blanchedalmond", high = "firebrick4", name = "Adverse effects normalized per 100,000 senior citizens", label = scales::comma) + theme(panel.background = element_rect(colour = "black")) + labs(title = "Distribution of COVID-19 vaccination adverse effects in US normalized for senior citizens", face = "bold")

aa + theme(text = element_text(size = 15))

