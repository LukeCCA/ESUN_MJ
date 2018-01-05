# ESUN_MJ
## 呼叫API方式
```
curl -"http://localhost:6010/GetRecommendationV1" GET -d "vid=<vid>"
```
## 測試
```
1. 起Docker Container服務： bash DockerLoad.sh
2. JMeter測試資料：./Test/vids.csv
3. JMeter回應資料：./Test/JMeterTest/TestLog
4. 測試目標：
    Response沒有出現Error
    Response的資料正確
```# MJ_TEST
