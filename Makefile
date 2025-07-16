IVY_DIR=/tmp/.ivy2

spark-submit:
	docker exec -it -u 1001:1001 -e HADOOP_USER_NAME=spark spark_master_container spark-submit \
		--master spark://spark-master:7077 \
		--conf spark.jars.ivy=$(IVY_DIR) \
		--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0,\
			org.apache.hadoop:hadoop-aws:3.3.4,\
			com.amazonaws:aws-java-sdk-bundle:1.12.787 \
		jobs/spark-city.py

kafka-producer:
	@echo "Running Kafka producer..."
	python jobs/main.py

help:
	@echo "make spark-submit     # Run the Spark Structured Streaming job inside Docker"
	@echo "make kafka-producer   # Run the Kafka test producer"