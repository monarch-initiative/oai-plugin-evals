library(jsonlite)
library(dplyr)
library(tidyr)
library(stringr)
library(ggplot2)
library(plotly)
library(htmlwidgets)


file_names <- list.files("../results", pattern = "trial-.*\\.json", full.names = TRUE)

# Then we can load the data into a list
data_raw <- lapply(file_names, jsonlite::fromJSON)

# that results in an unnamed list of entries; we need to parse out the file names and structure the list
# so that we can access it by question type and agent name


data_parsed <- lapply(seq_along(data_raw), function(i) {
	basics <- data_raw[[i]][c("module", "question", "goldstandard", "agent_name", "agent_answer", "agent_answer_num_function_calls", "eval_valuation")]
	x <- as.data.frame(basics, stringsAsFactors = FALSE)

	answer_prov <- data_raw[[i]]$agent_answer_provenance
	# if(is.data.frame(answer_prov)) {
	# 	answer_prov <- paste(answer_prov$content, collapse = "\n")
	# } else {
		answer_prov <- as.character(jsonlite::prettify(jsonlite::toJSON(answer_prov)))
	# }
	eval_prov <- as.character(jsonlite::prettify(jsonlite::toJSON(data_raw[[i]]$eval_provenance)))
	x$agent_answer_provenance <- answer_prov
	x$eval_provenance <- eval_prov
	x$filename <- basename(file_names[i])
	x
})

data_full <- bind_rows(data_parsed)
data <- data_full %>% select(-agent_answer_provenance, -eval_provenance)

`%+%` <- function(a, b) { paste0(a, b) }

