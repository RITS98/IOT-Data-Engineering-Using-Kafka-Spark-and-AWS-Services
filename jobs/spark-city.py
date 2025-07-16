from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType
import config


def main():
    spark = SparkSession.builder \
        .appName("IoT Data Engineering") \
        .config('spark.jars.packages', 
                'org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0,'
                'org.hadoop.aws:hadoop-aws:3.3.4,'
                'com.amazonaws:aws-java-sdk:1.12.787') \
        .config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem') \
        .config('spark.hadoop.fs.s3a.access.key', config.configuration['AWS_ACCESS_KEY']) \
        .config('spark.hadoop.fs.s3a.secret.key', config.configuration['AWS_SECRET_KEY']) \
        .config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
        .config('spark.hadoop.fs.s3a.endpoint', f"s3.{config.configuration['AWS_REGION']}.amazonaws.com") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Vehicle Data Schema
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True),
    ])

    # GPS Data Schema (fixed typo: vehicleType)
    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicleType", StringType(), True),
    ])

    # Traffic Camera Data Schema
    trafficSchema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("camera_id", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("snapshot", StringType(), True),
    ])

    # Weather Data Schema
    weatherSchema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("aqi", IntegerType(), True),
    ])

    # Emergency Incident Data Schema
    emergencySchema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("incident_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("severity", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True),
    ])

    # Function to read stream from Kafka
    def read_from_kafka(topic, schema):
        return (spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "broker:9092")
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(value AS STRING)")
            .select(from_json(col("value"), schema).alias("data"))
            .select("data.*")
            .withWatermark("timestamp", "2 minutes")
        )
    
    # Function to write stream to S3 in Parquet format
    def streamWriter(input_df, checkpointFolder, outputPath):
        return (input_df.writeStream
            .format("parquet")
            .option("checkpointLocation", checkpointFolder)
            .option("path", outputPath)
            .outputMode("append")
            .start()
        )
    
    # Reading from Kafka
    vehicleDF = read_from_kafka("vehicle_data", vehicleSchema)
    gpsDF = read_from_kafka("gps_data", gpsSchema)
    trafficDF = read_from_kafka("traffic_data", trafficSchema)
    weatherDF = read_from_kafka("weather_data", weatherSchema)
    emergencyDF = read_from_kafka("emergency_data", emergencySchema)

    # Writing to S3
    query1 = streamWriter(vehicleDF, "s3a://iot-data-bucket-ritayan/checkpoint/vehicle_data", "s3a://iot-data-bucket-ritayan/data/vehicle_data")
    query2 = streamWriter(gpsDF, "s3a://iot-data-bucket-ritayan/checkpoint/gps_data", "s3a://iot-data-bucket-ritayan/data/gps_data")
    query3 = streamWriter(trafficDF, "s3a://iot-data-bucket-ritayan/checkpoint/traffic_data", "s3a://iot-data-bucket-ritayan/data/traffic_data")
    query4 = streamWriter(weatherDF, "s3a://iot-data-bucket-ritayan/checkpoint/weather_data", "s3a://iot-data-bucket-ritayan/data/weather_data")
    query5 = streamWriter(emergencyDF, "s3a://iot-data-bucket-ritayan/checkpoint/emergency_data", "s3a://iot-data-bucket-ritayan/data/emergency_data")

    # Await all queries
    for query in [query1, query2, query3, query4, query5]:
        query.awaitTermination()


if __name__ == "__main__":
    main()