# ESUN_MJ
## 建模流程
```
1. 執行 /Demo3/TagPostgresql_ETL.py 來將資料存入Postgresql DB
2. 執行 /Demo3/InsertData_ETL.py 將資料存入Redis
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
測試相關檔案：\MJ_TEST
```