# ESUN_MJ
## Update Demo3 (有關Demo的全部放在Demo3資料夾內)
## Docker 啟動服務方法

1. 使用Dockerfile建立 tag_api:1.0 image
```
docker build -t tag_api:1.0 
```
2. 下載最新版本的redis
```
docker run -itd --name redis redis:latest
```
3. 下載Postgresql並修改其環境變數
```
docker run -itd --name postgres -e POSTGRES_PASSWORD=lukechen0419 -d postgres
```
4. 啟用Recommand System
```
docker run -itd --name chen_test -p 6010:6010 --link redis:redis --link postgres:postgres tag_api:1.0
```
## 在本機啟動服務方法
```
1. 需修改程式碼裡面有使用到Redis及Postgresql裡面的Host及Username等變數
2. 執行順序參照sh檔
```

## CF模型使用方法
```
Import Collobrative_Filtering.py 的 COLLOBORATIVE_FILTERING class
```
```
建模時使用fit module，\
input依序為userlog資料，offerlog資料另有兩個可自由輸入的參數，id_min及offer_min，\
id_min及offer_min為建模時第一層資料的篩選，\
id_min代表的為最少一個人最少需有的offer_tag數目，\
offer_min則為一個offer_tag最少被接觸到的人數，兩者預設均為1，\
其模型跑出的output為offer之ating table，\
另外也同時產出4個pickle檔，\
其內容分別為usertag的矩陣，offer rating table，offer tag的mapping table及tag mapping table
```
```
預測時使用predict module，input為redis所取出的顧客貼標庫資訊，output則為其前幾大(可自己設定)的offer tag，預設為15
```
