# ESUN_MJ
```
|——Demo3
|     |——
|      RecommendSystem
|        |——
|        Data
|           |—— MJ_TAG.xlsx
|           |__ Train_Data.csv
|
|        |—— Dockerfile
|        |—— Modeling.py  # Build Model
|        |—— Collobrative_Filtering.py  # CF Model
|        |—— CFRecommendation_API.py # Recommendation API
|        |—— requirements.txt
|        |__ start.sh # Docker excute shell file
|
|     |——
|      Simulation
|        |——Simulation.ipynb
|        |——CRV_recommender_simulation.ipynb
|           ......
|
|     |——
|      TagServer
|        |
|        Data
|           |—— INTENT_TAG.xlsx
|           |—— MJ_TAG.xlsx
|           |__ MJ_TAGVALUE.xlsx
|
|        |—— Dockerfile
|        |—— TagPostgresql_ETL.py  # Insert Tag Meta into postgresql
|        |—— InsertData_ETL.py  # Insert Data into Redis
|        |—— GetTags.py # Tag Server API
|        |—— requirements.txt
|        |__ start.sh # Docker excute shell file
|
|——MJ_TEST
|     |——
|      JMeterTest
|        |
|        |—— all_test_aws.jmx
|        |—— all_test_gcp.jmx
|        |—— all_test_azue.jmx
|        |__ vids.csv
|
|     |——
|      Unittest
|        |
|        |—— Collobrative_Filtering.py
|        |—— python_unittest.py # Use this to test function
|        |—— offer_testdata.csv
|        |__ user_testdata.csv
|
|——.travis.yml # unittest
|——docker-compose.yml
|__README.md

```
## 建模流程(只有建模)
```
1. 執行 /Demo3/TagServer/TagPostgresql_ETL.py 來將資料存入Postgresql DB
2. 執行 /Demo3/TagServer/InsertData_ETL.py 將資料存入Redis
3. 執行 /Demo3/RecommendSystem/Modeling.py
```

## 將Docker存出來的方法
```
docker save -o tag_api.tar tag_api:1.0 
docker save -o recommand_api.tar recommand_api:1.0 
```

## 測試
```
Docker Container服務： 在根目錄底下執行 docker-compose -d
測試相關檔案：/MJ_TEST
```