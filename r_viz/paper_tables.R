data_full$agent_listed_genes <- lapply(data_full$eval_provenance, jsonlite::fromJSON) %>% lapply(function(x){x$function_call$func_arguments$agent_answer %>% paste(collapse = ", ")}) %>% unlist()


#### Table 2 - differences between 3.5 + Monarch and 4-1106 + Monarch

data_full %>%
	mutate(agent_name = factor(agent_name,
														 levels = c("Dummy Agent GPT35", "Dummy Agent GPT4", "Dummy Agent GPT4 (1106-preview)", "Monarch Assistant GPT35", "Monarch Assistant GPT4", "Monarch Assistant GPT4 (1106-preview)"),
														 labels = c("3.5 Base", "4 Base", "4-1106 Base", "3.5 + Monarch", "4 + Monarch", "4-1106 + Monarch"),
														 ordered = TRUE)) %>%

	mutate(eval_valuation_bin =  case_when(eval_valuation == 1 ~ "1.0",
																				 eval_valuation == 0 ~ "0.0",
																				 0 < eval_valuation & eval_valuation <= 1/3 ~ "(0, 1/3]",
																				 1/3 < eval_valuation & eval_valuation <= 2/3 ~ "(1/3, 2/3]",
																				 2/3 < eval_valuation & eval_valuation < 1 ~ "(2/3, 1)",
																				 .default = NA

	)) %>%
	mutate(eval_valuation_bin = factor(eval_valuation_bin, levels = c("0.0", "(0, 1/3]", "(1/3, 2/3]", "(2/3, 1)", "1.0"), ordered = TRUE)) %>%
	mutate(`Score` = eval_valuation,
				 `Answer Genes` = agent_listed_genes,
				 `Module` = module,
				 `Question` = question,
				 `Gold Standard` = goldstandard,
				 `Agent Name` = agent_name) %>%
	select(`Module`, `Question`, `Gold Standard`, `Agent Name`, `Score`, `Answer Genes`) %>%
	pivot_wider(names_from = `Agent Name`, values_from = c(`Score`, `Answer Genes`), names_sep = ", ") %>%
	filter(`Score, 4-1106 + Monarch` != `Score, 3.5 + Monarch`) %>%
	arrange(desc(`Score, 4-1106 + Monarch` - `Score, 3.5 + Monarch`)) %>%
	select(`Module`, `Question`, `Gold Standard`, `Score, 4-1106 + Monarch`, `Answer Genes, 4-1106 + Monarch`, `Score, 3.5 + Monarch`, `Answer Genes, 3.5 + Monarch`) %>%
	write.table(file = "table2_4-1106-Monarch_vs_3.5-Monarch.txt", row.names = FALSE, col.names = TRUE, sep = "\t", quote = FALSE)

## Table 3 - Differences between 4-1106 + Monarch vs 4-1106 Base

data_full %>%
	mutate(agent_name = factor(agent_name,
														 levels = c("Dummy Agent GPT35", "Dummy Agent GPT4", "Dummy Agent GPT4 (1106-preview)", "Monarch Assistant GPT35", "Monarch Assistant GPT4", "Monarch Assistant GPT4 (1106-preview)"),
														 labels = c("3.5 Base", "4 Base", "4-1106 Base", "3.5 + Monarch", "4 + Monarch", "4-1106 + Monarch"),
														 ordered = TRUE)) %>%

	mutate(eval_valuation_bin =  case_when(eval_valuation == 1 ~ "1.0",
																				 eval_valuation == 0 ~ "0.0",
																				 0 < eval_valuation & eval_valuation <= 1/3 ~ "(0, 1/3]",
																				 1/3 < eval_valuation & eval_valuation <= 2/3 ~ "(1/3, 2/3]",
																				 2/3 < eval_valuation & eval_valuation < 1 ~ "(2/3, 1)",
																				 .default = NA

	)) %>%
	mutate(eval_valuation_bin = factor(eval_valuation_bin, levels = c("0.0", "(0, 1/3]", "(1/3, 2/3]", "(2/3, 1)", "1.0"), ordered = TRUE)) %>%
	mutate(`Score` = eval_valuation,
				 `Answer Genes` = agent_listed_genes,
				 `Module` = module,
				 `Question` = question,
				 `Gold Standard` = goldstandard,
				 `Agent Name` = agent_name) %>%
	select(`Module`, `Question`, `Gold Standard`, `Agent Name`, `Score`, `Answer Genes`) %>%
	pivot_wider(names_from = `Agent Name`, values_from = c(`Score`, `Answer Genes`), names_sep = ", ") %>%
	filter(`Score, 4-1106 + Monarch` != `Score, 4-1106 Base`) %>%
	arrange(desc(`Score, 4-1106 + Monarch` - `Score, 4-1106 Base`)) %>%
	select(`Module`, `Question`, `Gold Standard`, `Score, 4-1106 + Monarch`, `Answer Genes, 4-1106 + Monarch`, `Score, 4-1106 Base`, `Answer Genes, 4-1106 Base`) %>%
	write.table(file = "table3_4-1106-Monarch_vs_4-1106-Base.txt", row.names = FALSE, col.names = TRUE, sep = "\t", quote = FALSE)
