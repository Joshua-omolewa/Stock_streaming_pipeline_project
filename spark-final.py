#Created by Joshua Omolewa

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *


# This is boostrap server for MSK i.e. brokers

BOOTSTRAP_SERVERS='b-3.joshuamsk.yxngi1.c14.kafka.us-east-1.amazonaws.com:9092,b-2.joshuamsk.yxngi1.c14.kafka.us-east-1.amazonaws.com:9092,b-1.joshuamsk.yxngi1.c14.kafka.us-east-1.amazonaws.com:9092'


#HUDI CONFIGURATION SETTINGS
table_name = 'stock'
hudi_options = {
    'hoodie.table.name': table_name,
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
    'hoodie.datasource.write.recordkey.field': 'record_id',
    'hoodie.datasource.write.partitionpath.field': 'symbol',
    'hoodie.datasource.write.table.name': table_name,
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'event_time',
    'hoodie.datasource.write.hive_style_partitioning': 'true',
    'hoodie.datasource.hive_sync.partition_fields': 'true',
    'hoodie.datasource.hive_sync.database': "josh_stram_db",
    'hoodie.datasource.hive_sync.enable': 'true',
    'hoodie.datasource.hive_sync.table' : 'stock',
    'hoodie.datasource.hive_sync.support_timestamp': 'true',
    'hoodie.datasource.write.keygenerator.consistent.logical.timestamp.enabled': 'true',
    'hoodie.datasource.hive_sync.partition_fields' : 'symbol',
    'hoodie.datasource.hive_sync.partition_extractor_class' : 'org.apache.hudi.hive.MultiPartKeysValueExtractor',
    'hoodie.upsert.shuffle.parallelism': 100,
    'hoodie.insert.shuffle.parallelism': 100
    }

#PATH TO S3 FOLDER FOR TRANSFORED DATA
s3_path = "s3://streaming-project/transformed-data"



def write_batch(batch_df, batch_id):
    """
    function for writing tranformed kafka stream in batches
    then write to s3 in append mode
    """
    batch_df.write.format("org.apache.hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(s3_path)



if __name__ == "__main__":
    
    spark = SparkSession.builder.getOrCreate()

    # NOTE: we cant load the schema file from the local machine anymore, so we have to pull it from s3
    #.schema is to extract the schema from the json sample payload
    schema = spark.read.json('s3://streaming-project/schema/stock.json').schema 

    # We have to connect to the bootstrap servers, instead of kafka:9092
    df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) \
    .option("subscribe", "dbserver1.stream_db.stock") \
    .option("startingOffsets", "latest") \
    .load()


    transform_df = df.select(from_json(col("value").cast("string"), schema).alias("value"))



 

    


    #  TRANFORMING DATA INGESTED FROM KAFKA BROKERS
    transform_df = transform_df.select("value.payload.*")
    
    transform_df = transform_df \
        .withColumn("close", round(col("close"), 4)) \
        .withColumn("high", round(col("high"), 4)) \
        .withColumn("low", round(col("low"), 4)) \
        .withColumn("open", round(col("open"), 4)) \
        .withColumn("volume", col("volume").cast("double").cast(LongType())) \
        .withColumn("time", to_timestamp(col("time")/1000)) \
        .withColumn("event_time", to_timestamp(col("event_time")/1000))

    #checking schema
    transform_df.printSchema()




#  We cannot checkpoint to a local machine because we are working on the cloud. S3 is a reliable location for the cluster
    checkpoint_location = "s3://streaming-project/checkpoint/sparkjob"

    





#  Writing stream to start hoodie upsert
    transform_df.writeStream.option("checkpointLocation", checkpoint_location) \
        .queryName("josh stock") \
        .foreachBatch(write_batch) \
        .start().awaitTermination()



  

   