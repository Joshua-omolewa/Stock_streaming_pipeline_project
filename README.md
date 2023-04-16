# Real time Stock Streaming Data-pipeline (ETL) Project

# Author: 👤 **Joshua Omolewa**

## PROJECT OVERVIEW : I designed and implemented a real-time streaming pipeline to extract stock data from a stock API and build dashboards that monitor the stocks in real-time. The pipeline uses Apache Nifi for data ingestion and a MySQL database to store the data. To capture the changes in the database, I used Debezium, a Change Data Capture (CDC) tool that publishes the changes to a Kafka topic in Amazon MSK using the Debezium MySQL connector. The stock data in the Kafka topic is transformed using Spark Streaming and then loaded into the Glue database. I used Athena to query the Glue database to create real-time dashboards using Power BI and Tableau. The pipeline is orchestrated using Airflow, an open-source platform to programmatically author, schedule, and monitor workflows

##  Project Architecture

![project architecture](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Project%20Architecture.jpg)

## 1. Business Scenario
A Bank requires a data Engineer to build a streaming pipeline that tracks stocks in near real time and to develop a dashboard that tracks the changes in stock price in near real time.


## 2 STEPS USED TO COMPLETE THE PROJECT 

### Please note:The realtime stock streaming pipeline was built using  Python language. The pyspark script utilizes spark streaming and HUDI for transforming the stock data in the Amazon EMR cluster. 

* Built a stock API using FASTAPI framework that tracks Amazon and Apple stock gotten from  **[Aplha vantage](https://www.alphavantage.co/)** stock  **[API  (1min Intraday(extended history)](https://www.alphavantage.co/documentation/)** . The stock API is used to trigger airflow as soon as it recieves a get request for the stock data. Kindly find the sample query used to get the stock data from the Alphavantage stock API **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/download%20stock%20data%20from%20API.txt)** (Please note the API return data in CSV format). The stock data from Aplhavantage is stored in S3 which my stock API reads from. I created a landing page for my API using HTML & CSS as seen in the image below. The API is hosted using NGINX so the API is accessible anywhere in the world  and the API runs in Amazon EC2. The Fast API code can be found **[here](https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/api.py)**  . Please note other stock market API offer websocket protocol ( **[polygon.io](https://polygon.io/)** ,  **[Finnhub](https://finnhub.io/)** ) to ingest real time stock data but payment is required to have access hence I decided to create my own API with similar stock payload using Alphavantage Stock API which is free.
<img src="https://github.com/Joshua-omolewa/Stock_streaming_pipeline_project/blob/main/img/Stock%20API%20.jpg"  width="100%" height="100%"> 

* I then created an Amazon EC2 in which I hosted some docker containers for Apache Nifi, MySQL & Debezium. I built a data ingestion pipeline using Apache Nifi which ingest the stock data from my stock API and load the stock data into a MySQL database. I implemented  Change Data Capture (CDC) using debezium (with MySQL connector) which track the changes in the MySQL database and streams the changes to a kafka topic in Amazon MSK 


* Created a Input S3 (Amazon Simple Storage Service) bucket as a staging area for the raw data coming from the Snowflake. The raw data is extracted from the snowflake database using store procedure. Sample raw data from in the s3 bucket is shown in the image below. <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/raw%20data%20extracted%20to%20s3.jpg"  width="100%" height="100%">


* Utilized  Cloudwatch to pre-set a rule that automatically triggers the Lambda function at 12:05am MST as raw data extracted daily from snowflake  is expected in the s3 staging area by 12:00am MST . <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/cloudwatch%20rule.jpg"  width="100%" height="100%">

* Created the lambda function that cloudwatch triggers at 12:05am MST that scans the input s3 bucket (staging area) for yestedays raw daw and if found the lamda function triggers airflow workflow automatically to start the batch processing. Also if the data is not yet available an email is sent to notify the data engineer that the data from the transactional database has not been received. The python code for the lambda function can be found **[here](https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/lambda_function.py)** while the email python code for the lambda function can be found **[here](https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/send_email.py)** <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/lambda%20function%20to%20trigger%20airflow%20and%20send%20email.jpg"  width="100%" height="100%">

* Created docker containers runing Airflow using docker compost  within an EC2 (Amazon Elastic Compute Cloud) instance. Ariflow is used to orchestrate & schedule the the movement of data from S3 to the Amazon EMR cluster for transformation. Airflow submits the spark job to the EMR clust and also monitor the spark job transformation step in the EMR cluster and displays if the EMR steps executed successfully in DAG Graph view. The airflow python code for the airflow dags can be found **[here](https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/airflow_dag.py)**  <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/Airflow.jpg"  width="100%" height="100%">

* Created an Amazon EMR cluster that has hadoop & spark frameworks installed. The EMR will transform the raw data utitizing pyspark based on the spark submit configuration received from airflow using  to meet the business requirement  and load the transform data in parquet format to the output S3  bucket (ETL process). The pyspark scripts for the project can be found  **[here](https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/tree/main/spark_files)**  <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/emr%20runing%20spark%20submit%20job.jpg"  width="100%" height="100%">

* Created an Output S3 bucket which the transformed data from EMR Cluster is stored.<img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/tranformed%20s3%20bucket.jpg"  width="100%" height="100%">

* Utilized Glue to automatically crawl the output S3 bucket to create tables in the Glue catalog/database that can be queried using Athena by the data analyst .<img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/AWS%20glue%20crawler%20final.jpg"  width="100%" height="100%">

* Made use of athena to query the tables created using Glue. The Data anlyst can interact with the weekly fact table using SQL in order to answer business questions. <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/Anthena%20final.jpg"  width="100%" height="100%">


* Finally I created a docker container that runs superset in an EC2 instance. Superset can be used to create Data Visualization  & dashboards  by the Data Analyst. <img src="https://github.com/Joshua-omolewa/end-2-end_data_pipeline_project/blob/main/img/Superset%20finals.jpg"  width="100%" height="100%">

# Follow Me On
  
* LinkedIn: [@omolewajoshua](https://www.linkedin.com/in/joshuaomolewa/)  
* Github: [@joshua-omolewa](https://github.com/Joshua-omolewa)


## Show your support

Give a ⭐️ if this project helped you!
