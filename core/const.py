MAX_ROUND = 20  # max try times of one agent talk
# DESC_LEN_LIMIT = 200  # max length of description of each column (counted by char)
# MAX_OUTPUT_LEN = 1000  # max length of output (counted by tokens)
# RATIO = 0.8  # soft upper bound of max

ENGINE_GPT4 = 'gpt-4'
ENGINE_GPT4_32K = 'gpt-4-32k'

GUDING_NAME = 'Guiding'
INSIGHT_NAME = 'Insight'
REFINER_NAME = 'Refiner'
SYSTEM_NAME = 'System'
DATA_NAME = 'Data'
MEMORY_NAME = 'Memory'



guider_template = """
As an experienced and professional data scientist, you job is to review a user's goal (Input) and the structure of a database table,then guidance on how to extract useful insights to achieve that goal.
The table schema consists of multiple column descriptions. 

[Instruction]:
1. If the provided insights fulfill the user's goal, you should mark the state as "FINISHED" in your output. Otherwise, mark it as "CONTINUE".
2. If the state is "CONTINUE", You need to pushish the task for extracting the insights to achieve that goal.
3. The output should be in JSON format.

Requirements:
1. You need to first check if the provided insights are enough to complete the user's goal.
2. Prioritize the columns in each relevant table based on their relevance.
3. The output task should not same as the goal.
4. No other texts are required.

Here is an input format:
【table_name】 {db_id}
【Schema】
{desc_str}
【Goal】
{query}
【Insights】
{insights}
Here is an output example:
【Answer】
```json
{{
  "task": "Analyze the variation of crime rates over time across different districts and types of crime to identify any patterns, trends, or anomalies",
  "interesting_columns": ["timestamp", "year", "dstrict", "council_district_code", "primary_type"],
  "state": "FINISHED"
}}
```

==========

"""

subq_pattern = r"Sub question\s*\d+\s*:"

data_template = """
You are a skilled SQL query developer and data scientist. Your task involves utilizing the provided table schema, relevant columns, the information of the needed data, and analysis history to generate SQL (based on the SQL template) for completing the data analysis task. 
The table schema consists of multiple column descriptions. 

[SQL Template]:
SELECT DC, ..., DC, $\psi(MC)$
FROM T
WHERE $(\phi)$
GROUP BY DC, ..., DC
ORDER BY  $\psi(MC)$ DESC
Predicate $\phi$ := DC = s | $\phi \cap \psi$
Aggregation $\psi$ := SUM | AVG | COUNT | ...

Where dimension columns (denoted DC) and measure columns (denoted MC). Our language considers queries of the same structure: they select some columns from an
input table, fltered by a predicate $\phi$; the resulting table is grouped by certain dimension columns and ordered by a particular measurecolumn. 
Our language allows using aggregations, such as SUM, AVG, COUNT. Predicates in our language can refer to a string s.

[Instruction]:
1. If the "Input SQL" is not empty, you should transfer this SQL to new SQL, which is based on the SQL template, and analysis history and follow four types of transformations.
2. If the "Input SQL" is empty, you should generate a new SQL.

[Four types of transformations]:
1.Replacing measure column : we consider transformationsthat replace MC with another measure column MC' in the sametable. Prioritize the columns in table based on their relevance for the analysing task.
2.Changing dimension column : we also consider replacing one of the dimension columns in table with another dimensioncolumn in the same table.
3. Transforming aggregation.The aggregation function $\psi$ used in P may also get transformed to another.
4. Rewriting flter:  A flter DC = s in table may get rewritten to another flter. We consider all filters of the same shape butwith different dimension columns or values from the same table.

Requirements:
1. The generated SQL must follow the given SQL Template.
3. No other texts are required.
3. Only one type of transformer will be used.



==========

Here is an input format:

【Database schema】
{desc_str}
【Task】
{task}
【Relevant columnsl】
{relevant_column}
【Input SQL】
{sql}
【Prefer data】
{prefer_data}
【Analysis history】 
{analysis_trajs}


Here is an output example:

【SQL】

```sql
"SELECT
    YEAR(timestamp) AS year,
    district,
    council_district_code,
    primary_type,
    location_description,
    COUNT(*) AS total_crimes,
    AVG(latitude) AS avg_latitude,
    AVG(longitude) AS avg_longitude
FROM austin_crime
WHERE timestamp IS NOT NULL
GROUP BY YEAR(timestamp), district, council_district_code, primary_type, location_description
ORDER BY year, district, total_crimes DESC;"
```

==================
Now please generate new SQL.
【SQL】
"""

insight_template = """
As a data analysis professional, your task is to analyze data and summarize insights. 
The analysis history is available.

[Instruction]:
1. Review the history analysis and the current input table. Decide if it is enough for your analysis.
2. If you need more data, please (1) give the analysis for the input table based on the analysis history;
(2) list what you need (i.e., prefer_data in the output) and update the interesting conlumns if needed. 
3. You need to rate your analysis based on the analysis history and your knowledge.
4. The output should be in JSON format.
5. *** You must offer a refined insight without merely stating a relationship exists. *** 

[Ranking]:
Please use a scale from 1 to 5 to rate the analysis provided in this step.
1: Only hypothesis.
2: Reasonable decision.
3: Modest decision.
4: Confidence.
5: Very confidence.


[requirements]:
1. Non-empty Analysis: Ensure the 'analysis_output' field is not left blank and must include the rate for your analysis.
2. Analysis History Condition: If the analysis history's length is less than 2, the 'insight' should remain an empty string.
3. Simplified Response: No additional text is provided outside the JSON structure.
4. Insight Summarization: If the information (or provided data) is sufficient, please only point out what the insight isin the 'insight' field; otherwise, leave it as an empty string.
5. No other texts are needed in the "insight" field, if if you need more data to verify this insight, please leave it as an empty string and set the "perfer data".

Here is  a bad example:

"insight": The effectiveness of law enforcement in solving different types of crimes can be better understood by analyzing the correlation between clearance status and crime types.

Please not output the insight like above.
The true insight requires detailing the how and why behind the varying success of law enforcement in solving different types of crimes, backed by specific examples and evidence.


==========

Here is an input format:

【Database schema】
{desc_str}
【Task】
{task}
【Input table】
{table}
【Analysis history】 
{analysis_trajs}
【Relevant columnsl】
{relevant_column}

Here is an output example:

【Output】
```json
{{
  "analysis_output": ["The hourse price in Beijing is incresing from 2010 to 2020", "4"], 
  "insight": " Beijing has the most highest price in all cities in China",
  "prefer_data": "We need more data about the price in Shanghai",
  "interesting_columns": ["timestamp", "year", "dstrict", "council_district_code", "primary_type"]
  }}
```

Here is an another output example:
```json
{{
  "analysis_output": ['There is a correlation between clearance status and crime types based on the provided data', '3'] 
  "insight": "",
  "prefer_data": "We need more data about the crimes in Shenzhen",
  "interesting_columns": ["timestamp", "council_district_code", "primary_type"]
  }}
```

==========================



================
Now, please start your analysis:
"""

refiner_template = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Solve the task step by step if you need to. Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values
【Query】
-- {query}
【Evidence】
{evidence}
【Database info】
{desc_str}
【Foreign keys】
{fk_str}
【old SQL】
```sql
{sql}
```
【SQLite error】 
{sqlite_error}
【Exception class】
{exception_class}

Now please fixup old SQL and generate new SQL again.
【correct SQL】
"""


memory_template = """
As a professional data analyst, you are required to update the entire insight memory based on newly inputted insights.

The insight memory contains multiple insights that have been acquired.

[Instruction]:
1. If the newly added insight can be merged with an existing insight in the memory, then merge them;
2. If not, create a new insight within the memory and insert the new insight into it;
3. You also need to check whether there are any insights in the insight memory that can be merged to yield more specific and interesting insights; if they cannot be merged, then it is not necessary;
4. The output should be in JSON format.


[requirements]:
1. You need to output the updated insight memory.
2. You need to carefully check whether the insight should be merged with an existing insight in the memory. If you are not confident about it, please do not merge it.
3. You should also output your action (i.e, insert or merge).
4. No other text is needed.


===========================
Here is an input format:
【Insight】
{insight}
【Insight Memory】
{insight_memory}


=================
Here is an example:

【Input】
Insight: "Theft is the most common type of crime across all districts"
Insight Memory: ["District D having the highest number of theft incidents", "The presence of anomalies in the data, such as a sudden spike in a specific type of crime at a particular location", "Certain locations, particularly malls and shopping centers, are hotspots for shoplifting and theft due to high foot traffic and the availability of valuables"]

【Output】
Insight_Memory: ["Theft is the most common type of crime across all districts with District D having the highest number of theft incidents", "The presence of anomalies in the data, such as a sudden spike in a specific type of crime at a particular location", "Certain locations, particularly malls and shopping centers, are hotspots for shoplifting and theft due to high foot traffic and the availability of valuables"]
Action: Merge

Here is an another example:
【Input】
Insight: "The housing prices in first-tier cities are rising."
Insight Memory: ["The level of education is directly proportional to income.", "The income in IT and financial industries is higher than in other industries."]

【Output】
Insight_Memory:  ["The housing prices in first-tier cities are rising.", "The level of education is directly proportional to income.", "The income in IT and financial industries is higher than in other industries."]
Action: Insert

Here is an output example:

【Output】
```json
{{
  "insight_memory": ["The housing prices in first-tier cities are rising.", "The level of education is directly proportional to income.", "The income in IT and financial industries is higher than in other industries."],
  "Action": "Insert
}}
```

Now please update the insight_memory:
"""