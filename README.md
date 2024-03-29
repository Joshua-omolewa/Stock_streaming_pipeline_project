# Real time Stock Streaming Data-pipeline (ETL) Project

![Spark](https://img.shields.io/badge/Apache-Spark-lightgrey)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000?style=for-the-badge&logo=apachekafka)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Nifi](https://img.shields.io/badge/Apache-NIFI-yellowgreen)

# Author: 👤 **Joshua Omolewa**

## PROJECT OVERVIEW: I designed and implemented a real-time streaming pipeline to extract stock data from a stock API and build dashboards that monitor the stocks in real time. The pipeline uses Apache Nifi for data ingestion and a MySQL database to store the data. To capture the changes in the database, I used Debezium, a Change Data Capture (CDC) tool that publishes the changes to a Kafka topic in Amazon MSK using the Debezium MySQL connector. The stock data in the Kafka topic is transformed using Spark Streaming and then loaded into the Glue database. I used Athena to query the Glue database to create real-time dashboards using Power BI and Tableau. The pipeline is orchestrated using Airflow, an open-source platform to programmatically author, schedule, and monitor workflows

## LIVE VIDEO DEMO OF THE PROJECT CAN BE FOUND  **[HERE](https://www.youtube.com/watch?v=hy595CJ7j_g&t=1011s)**

##  Project Architecture

![project architecture](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Project%20Architecture.jpg)

## 1. Business Scenario
A Bank requires a Data Engineer to build a streaming pipeline that tracks stocks in near real-time and to develop a dashboard that tracks the changes in stock price in near real-time.


## 2. STEPS USED TO COMPLETE THE PROJECT 

### Please note: The real-time stock streaming pipeline was built using  Python language. The pyspark script utilizes spark streaming and HUDI for transforming the stock data in the Amazon EMR cluster. 

* Built a stock API using the FASTAPI framework that tracks Amazon and Apple stock gotten from  **[Alpha vantage](https://www.alphavantage.co/)** stock  **[API  (1min Intraday(extended history)](https://www.alphavantage.co/documentation/)** . The stock API is used to trigger airflow as soon as it  receives a get request for the stock data. Kindly find the sample query used to get the stock data from the Alphavantage stock API **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/download%20stock%20data%20from%20API.txt)** (Please note the API return data in CSV format). The stock data from Alphavantage is stored in S3 which my stock API reads from. I created a landing page for my API using HTML & CSS as seen in the image below. The API is hosted using NGINX as a web server, so it is accessible anywhere in the world, and it runs in Amazon EC2. The Fast API code can be found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/api.py)**. Please note that other stock market APIs offer the websocket protocol ( **[polygon.io](https://polygon.io/)** ,  **[Finnhub](https://finnhub.io/)** ) to ingest real-time stock data, but payment is required to have access; hence, I decided to create my  API with a similar stock payload using the Alphavantage Stock API which is free. 
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Stock%20API%20.jpg"  width="100%" height="100%"> 

* I then created an Amazon EC2 instance in which I hosted some docker containers for Apache Nifi, MySQL & Debezium. I built a data ingestion pipeline using Apache Nifi ( see Apache Nifi Architecture in the image below) which ingests the stock data from my stock API and inserts the stock data into a MySQL database. The DDL statement used to create the stock table in the MySql database can be found  **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/stock%20DML.sql)** . I implemented  Change Data Capture (CDC) using debezium (with MySQL connector) which track the changes in the MySQL database and streams the changes to a Kafka topic in Amazon MSK. My Apache Nifi template architecture can be found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/Joshua-final-stocks-nifi.xml)** . The client URL (CURL) command used for the debezium mySQL connector which is responsible for tracking the changes in the Mysql database and creating the Kafka topics in MSK is

```
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{ "name": "stock-connector", "config": { "connector.class": "io.debezium.connector.mysql.MySqlConnector", "tasks.max": "1", "database.hostname": "mysql", "database.port": "3306", "database.user": "root", "database.password": "debezium", "database.server.id": "184054", "database.server.name": "dbserver1", "database.include.list": "<database name>", "database.history.kafka.bootstrap.servers": "'"<broker url>"'", "database.history.kafka.topic": "dbhistory.<database name>" } }' 
```
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Docker%2C%20MYSQL%2C%20Apache%20Nifi%2C%20Kafka.jpg"  width="100%" height="100%"> 
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Apache%20Nifi%20Architecture.jpg"  width="100%" height="100%"> 

* Created docker containers running Airflow using docker compost  within an EC2 (Amazon Elastic Compute Cloud) instance. The stock API trigger airflow as soon as stock data is ingested by Apache Nifi. Airflow is used to trigger the lambda function, which sends a post request to submit the spark job to the Amazon EMR cluster using a post request sent to Livy. Airflow monitor the spark job through Livy to ensure the spark job did not fail in the EMR cluster. The airflow python code for the airflow dags can be found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/aiflowlambda.py)** 
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Ariflow.jpg"  width="100%" height="100%"> 

* I also created a lambda function that submits the spark job to the EMR cluster through livy once it is triggered by airflow. Livy is a rest interface that helps in interacting with the spark cluster. The EMR cluster was created with livy pre-installed . The spark streaming Python code can be found here **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/spark-final.py)**. The lambda function code used to send post requests to livy can be found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/lamda_function.py)**. Also, I wrote a lambda function code  used to delete the spark job in case I want to restart the API and stop all spark jobs running in the EMR cluster found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/lamda_function2.py)**
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Livy%20%2C%20EMR%2C%20Lambda%20function.jpg"  width="100%" height="100%"> 

* I created Amazon Managed Streaming for Apache Kafka (MSK) in which the Kafka topics are created by debezium. The stock stream data is sent from the debezium MySQL connector to the Kafka topic, and the spark streaming job also ingests data from the Kafka topic for stream processing. The transformed data from the spark streaming job is loaded into the S3 in hudi format.  <img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/S3%20transformed%20data%20%26%20MSk.jpg"  width="100%" height="100%">


* I created a database called stock in glue, which contains the table created from the hudi upsert when the spark streaming job is running in the EMR cluster. Glue reads the stock data from the transformed s3 bucket automatically. The stock table in the glue database can be read by Athena automatically. <img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Amazon%20Glue%20%26%20Athena.jpg"  width="100%" height="100%">


* I performed a data quality check using great expectations on the final transformed stock data to ensure there is no deviation in the stock data expected. I checked for the presence of null values, checked that some columns are present, checked that the table is not empty, and validated the data type for the time column. Also, I configured the generation of a slack notification when performing the data quality check. <img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Data%20quality%20check%20.jpg"  width="100%" height="100%">
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Great%20expectation%20data%20doc%20website.jpg"  width="100%" height="100%">


* Finally, I created a near real-time stock candlestick dashboard (updated every 30 seconds) to track Amazon and Apple stock  using PowerBI and Tableau. The candlestick dashboard extracts stock data from the Athena stock table. The Live tableau dashboard can be seen **[here (Click here to see the public tableau dashboard)](https://public.tableau.com/app/profile/joshua5804/viz/stock_16779988822150/Dashboard1?publish=yes)**. <img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/PowerBI%20%26%20Tableau%20dashboard.jpg"  width="100%" height="100%">

# Follow Me On
  
* LinkedIn: [@omolewajoshua](https://www.linkedin.com/in/joshuaomolewa/)  
* Github: [@joshua-omolewa](https://github.com/Joshua-omolewa)


## Show your support

Give a ⭐️ if this project helped you!
