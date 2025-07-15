# IOT-Data-Engineering-Using-Kafka-Spark-and-AWS-Services






## Setup Steps

### Create Docker containers
1. Create a `docker-compose.yml` to create kafka and spark containers.

```
version: '3.8'  # Use Docker Compose version 3.8 for better networking and healthcheck features

# ------------------------------------------------------------------------------
# Shared Spark Configuration
# ------------------------------------------------------------------------------
# Using YAML anchors (&spark-common) and references (<<: *spark-common)
# to define reusable configuration for Spark workers.
x-spark-common: &spark-common
  image: bitnami/spark:latest  # Official Bitnami Spark image with minimal dependencies
  volumes:
    - ./jobs:/opt/bitnami/spark/jobs  # Mount local directory for Spark jobs or scripts
  command: bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
  depends_on:
    spark-master:
      condition: service_healthy  # Ensure Spark master is up before starting workers
  environment:
    SPARK_MODE: Worker               # Run container in Spark Worker mode
    SPARK_WORKER_CORES: 2           # Limit each worker to 2 CPU cores
    SPARK_WORKER_MEMORY: 2g         # Allocate 2 GB of memory per worker
    SPARK_MASTER_URL: spark://spark-master:7077  # Address of the master node
  networks:
    - my_network  # All containers share the same virtual network

services:

  # ------------------------------------------------------------------------------
  # Zookeeper (required for Kafka coordination)
  # ------------------------------------------------------------------------------
  zookeeper:
    container_name: zookeeper_container
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    ports:
      - "2181:2181"  # Expose Zookeeper client port to host
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000  # Basic timing unit used for Zookeeper heartbeats
    healthcheck:
      test: ["CMD", "bash", "-c", "echo 'ruok' | nc localhost 2181"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - my_network

  # ------------------------------------------------------------------------------
  # Kafka Broker (uses Zookeeper for coordination)
  # ------------------------------------------------------------------------------
  broker:
    container_name: kafka_container
    image: confluentinc/cp-server:7.4.0  # Full Confluent Kafka broker
    hostname: broker
    depends_on:
      zookeeper:
        condition: service_healthy  # Start Kafka only after Zookeeper is healthy
    ports:
      - "9092:9092"     # Host-to-container Kafka access
      - "9101:9101"     # JMX port for monitoring Kafka internals
    environment:
      # Core Kafka configuration
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'  # Connect to Zookeeper
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1  # Suitable for single-node clusters

      # Optional: Confluent monitoring and licensing
      KAFKA_METRICS_REPORTERS: io.confluent.metrics.reporter.ConfluentMetricsReporter
      KAFKA_CONFLUENT_LICENSE_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_CONFLUENT_BALANCER_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1

      # JMX monitoring
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost

      # Confluent metrics reporting (disabled)
      KAFKA_CONFLUENT_SCHEMA_REGISTRY_URL: http://schema-registry:8081
      CONFLUENT_METRICS_REPORTER_BOOTSTRAP_SERVERS: broker:29092
      CONFLUENT_METRICS_REPORTER_TOPIC_REPLICAS: 1
      CONFLUENT_METRICS_ENABLE: 'false'
      CONFLUENT_SUPPORT_CUSTOMER_ID: 'anonymous'
    healthcheck:
      test: ["CMD", "bash", "-c", "nc -z localhost 9092"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - my_network

  # ------------------------------------------------------------------------------
  # Spark Master Node
  # ------------------------------------------------------------------------------
  spark-master:
    container_name: spark_master_container
    image: bitnami/spark:latest
    volumes:
      - ./jobs:/opt/bitnami/spark/jobs  # Same volume as workers
    command: bin/spark-class org.apache.spark.deploy.master.Master
    ports:
      - "9090:8080"  # Spark Web UI
      - "7077:7077"  # Spark internal port for worker registration
    healthcheck:
      # Check if Spark UI port is responsive
      test: ["CMD-SHELL", "timeout 2 bash -c '</dev/tcp/localhost/8080'"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - my_network

  # ------------------------------------------------------------------------------
  # Spark Worker 1 (inherits from spark-common)
  # ------------------------------------------------------------------------------
  spark-worker-1:
    <<: *spark-common
    container_name: spark_worker_1_container

  # ------------------------------------------------------------------------------
  # Spark Worker 2 (inherits from spark-common)
  # ------------------------------------------------------------------------------
  spark-worker-2:
    <<: *spark-common
    container_name: spark_worker_2_container

  # ------------------------------------------------------------------------------
  # OPTIONAL: PostgreSQL database for Airflow backend
  # ------------------------------------------------------------------------------
  # db:
  #   container_name: postgres_container
  #   image: postgres:14
  #   environment:
  #     POSTGRES_USER: airflow
  #     POSTGRES_PASSWORD: airflow
  #     POSTGRES_DB: airflow_db
  #   ports:
  #     - "5421:5432"  # Avoid default 5432 to reduce port conflict risk
  #   volumes:
  #     - ./postgres/data:/var/lib/postgresql/data
  #   healthcheck:
  #     test: ["CMD-SHELL", "pg_isready -U airflow -d airflow_db"]
  #     interval: 5s
  #     timeout: 5s
  #     retries: 5
  #   networks:
  #     - my_network

  # ------------------------------------------------------------------------------
  # OPTIONAL: Apache Airflow for orchestrating ETL jobs
  # ------------------------------------------------------------------------------
  # airflow:
  #   container_name: airflow_container
  #   image: apache/airflow:2.8.0
  #   ports:
  #     - "8063:8080"  # Airflow web UI
  #   environment:
  #     AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@db:5432/airflow_db
  #     PYTHONPATH: /opt/airflow  # Ensures Python code in /code is importable
  #   env_file:
  #     - .env
  #   restart: unless-stopped
  #   volumes:
  #     - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
  #     - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
  #     - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
  #     - ${AIRFLOW_PROJ_DIR:-.}/requirements.txt:/opt/airflow/requirements.txt
  #     - ${AIRFLOW_PROJ_DIR:-.}/code:/opt/airflow/code
  #   command: >
  #     bash -c "
  #     pip install -r /opt/airflow/requirements.txt &&
  #     airflow db migrate &&
  #     airflow standalone
  #     "
  #   depends_on:
  #     db:
  #       condition: service_healthy
  #   networks:
  #     - my_network

# ------------------------------------------------------------------------------
# Docker Bridge Network
# ------------------------------------------------------------------------------
# All services communicate over this isolated bridge network
networks:
  my_network:
    driver: bridge

```

2. Run the containers using `docker compose up --build` (first time) next time just use `docker-compose up`
3. To stop the container use `docker compose down`

### Check data is getting published to Kafka

1. Run the code in isolation present in `jobs/main.py`
2. It contains mock data generator to generate data from sinthesized sources.
3. On successfull producing the data to Kafka, the terminal looks like this
<img width="635" height="234" alt="image" src="https://github.com/user-attachments/assets/38eacf8c-75c9-4758-b725-a60e2f5fe8f3" />

4. Check for the data in the Kafka topic.
5. Go to the Docker Desktop and click on `exec` tab of the kafka container.
6. Run the commangs as shown below.
<img width="1257" height="709" alt="image" src="https://github.com/user-attachments/assets/d5a371df-d246-48e2-8486-c5e2b9c8b0a8" />





### Create a connection in Apache Airflow
1. Go to Admin -> Connections -> Add Connection
2. Give a name
3. Add the credentials.
If the AWS credentials is already set in the local computer, we can get it using -
`aws configure export-credentials`
<img width="1695" height="864" alt="image" src="https://github.com/user-attachments/assets/cdf59926-3ac6-46e1-9b95-c0300bbeda48" />

<img width="1692" height="287" alt="image" src="https://github.com/user-attachments/assets/9f17acd7-b867-4720-bdd1-5cef2bd24316" />

To set up AWS credentials in local computer, follow the below steps
1. Go to IAM service in AWS
2. Click on `My Quick Credentials`
<img width="1676" height="813" alt="image" src="https://github.com/user-attachments/assets/4b8d9e36-1c07-4576-9ace-285836d2999b" />
3. Create a Access Key as given below
<img width="1676" height="787" alt="image" src="https://github.com/user-attachments/assets/c166990e-22de-4ee8-b5f8-2cc66cf126c8" />
4. Set up the credentials in local environment
```
export AWS_ACCESS_KEY_ID=[YOUR ACCESS KEY]
export AWS_SECRET_ACCESS_KEY=[YOUR SECRET KEY]
export AWS_DEFAULT_REGION=[YOUR REGION]
```

5. Check if it is working
```
aws s3 ls  # list s3 buckets, should not throw an error
```


### Create AWS S3 Bucket
1. Go to S3 service in AWS.
2. Click on `Create Bucket`.
3. Fill the Create Bucket application as given below and click on `Create Bucket`
<img width="3342" height="4361" alt="image" src="https://github.com/user-attachments/assets/5a379fa6-13ec-4484-97db-9f21b7d23e31" />

<img width="1110" height="311" alt="image" src="https://github.com/user-attachments/assets/73391ac8-1c6d-4fd8-b8b7-a139763b8e9c" />
