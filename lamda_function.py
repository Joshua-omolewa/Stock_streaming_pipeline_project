import json
import random
from random import *
import boto3
import requests
import lamda_function2 as del_sparkjob  #importing the second lambda function used for deleting spark jobs

#implementing this curl command below using lambda

"""
curl -X POST -H "Content-Type: application/json" -d '{
    "file": "s3://streaming-project/spark-stream-code/spark-new.py",
    "className": "org.apache.spark.deploy.SparkSubmit",
    "name": "stremaing-app1",
    "conf": {
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.hudi.catalog.HoodieCatalog",
        "spark.sql.extensions": "org.apache.spark.sql.hudi.HoodieSparkSessionExtension",
        "spark.jars.packages": "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0"
    },
    "jars": ["s3://streaming-project/jar/hudi-spark-bundle.jar"]
}' http://<master node-Master public DNS>:8998/batches

"""




def lambda_handler(event, context):
    """
    This lambda function submits the spark job using Livy.
    It sends a post request to livy endpoint
    """
    # Defining request parameters need
    endpoint_url = "http://ec2-50-17-26-47.compute-1.amazonaws.com:8998/batches"
    headers = {"Content-Type": "application/json"}
    data = {
        "file": "s3://streaming-project/spark-stream-code/spark-new.py",
        "className": "org.apache.spark.deploy.SparkSubmit",
        "conf": {
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.hudi.catalog.HoodieCatalog",
            "spark.sql.extensions": "org.apache.spark.sql.hudi.HoodieSparkSessionExtension",
            "spark.jars.packages": "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
            "spark.submit.deployMode": "client"
        },
        "jars": ["s3://streaming-project/jar/hudi-spark-bundle.jar"]
    }


    try:
        
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
    
        return {
            "statusCode": response.status_code,
            "body": response.text
            
        }
    except Exception as e:
        
        print(f"Error connecting to Livy: {e}")
        raise e
        
#code below to manually delete & stop all spark jobs using livy rest url

# def lambda_handler(event, context):
#     url = "http://ec2-34-207-210-96.compute-1.amazonaws.com:8998"
#     del_sparkjob.del_all_livy_batches(url)