#!/bin/bash
python TagPostgresql_ETL.py
python InsertData_ETL.py
python GetTags.py &
python CFRecommendation_API.py 