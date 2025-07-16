# IOT-Data-Engineering-Using-Kafka-Spark-and-AWS-Services

## Project Overview
This is a comprehensive Real-time IoT Data Engineering Pipeline that simulates smart city data processing using modern big data technologies. The project demonstrates an end-to-end data pipeline from data generation to analytics-ready storage.

## Architecture & Technology Stack

### Core Technologies:
1. Apache Kafka - Real-time data streaming and message queuing
2. Apache Spark - Distributed data processing and stream analytics
3. Docker - Containerized infrastructure
4. AWS Services - Cloud storage and analytics (S3, Glue, Redshift)
5. Python - Data generation and processing logic

### Infrastructure Components:
1. Kafka Ecosystem
    - Zookeeper for coordination
    - Kafka broker for message streaming
    - Multiple topics for different data types

2. Spark Cluster
    - Spark Master node
    - 2 Spark Worker nodes (2 cores, 2GB RAM each)
    - Structured streaming for real-time processing

3. Containerized Environment

    - Docker Compose orchestration  
    - Health checks and service dependencies
    - Volume mounts for code sharing

### Architecture Diagram
```
graph TB
    %% Data Sources
    subgraph "IoT Data Sources"
        VS[Vehicle Sensors]
        GPS[GPS Trackers]
        TC[Traffic Cameras]
        WS[Weather Stations]
        ES[Emergency Systems]
    end

    %% Data Generation Layer
    subgraph "Data Generation Layer"
        DG[Data Generator<br/>main.py]
        VS --> DG
        GPS --> DG
        TC --> DG
        WS --> DG
        ES --> DG
    end

    %% Message Streaming Layer
    subgraph "Kafka Streaming Platform"
        ZK[Zookeeper<br/>Port: 2181]
        KB[Kafka Broker<br/>Port: 9092]
        
        subgraph "Kafka Topics"
            VT[vehicle_data]
            GT[gps_data]
            TT[traffic_data]
            WT[weather_data]
            ET[emergency_data]
        end
        
        ZK --> KB
        KB --> VT
        KB --> GT
        KB --> TT
        KB --> WT
        KB --> ET
    end

    %% Spark Processing Layer
    subgraph "Spark Cluster"
        SM[Spark Master<br/>Port: 7077<br/>UI: 9090]
        SW1[Spark Worker 1<br/>2 cores, 2GB RAM]
        SW2[Spark Worker 2<br/>2 cores, 2GB RAM]
        
        subgraph "Spark Streaming Job"
            SSJ[spark-city.py<br/>Structured Streaming]
            
            subgraph "Data Schemas"
                VSch[Vehicle Schema]
                GSch[GPS Schema]
                TSch[Traffic Schema]
                WSch[Weather Schema]
                ESch[Emergency Schema]
            end
            
            subgraph "Stream Processing"
                SP[Schema Validation]
                WM[Watermarking<br/>2 min window]
                TR[Transformations]
            end
        end
        
        SM --> SW1
        SM --> SW2
        SW1 --> SSJ
        SW2 --> SSJ
    end

    %% AWS Cloud Layer
    subgraph "AWS Cloud Services"
        subgraph "Data Lake (S3)"
            S3[S3 Bucket<br/>iot-data-bucket-ritayan]
            
            subgraph "Data Folders"
                VDF[/data/vehicle_data/]
                GDF[/data/gps_data/]
                TDF[/data/traffic_data/]
                WDF[/data/weather_data/]
                EDF[/data/emergency_data/]
            end
            
            subgraph "Checkpoint Folders"
                VCF[/checkpoint/vehicle_data/]
                GCF[/checkpoint/gps_data/]
                TCF[/checkpoint/traffic_data/]
                WCF[/checkpoint/weather_data/]
                ECF[/checkpoint/emergency_data/]
            end
            
            S3 --> VDF
            S3 --> GDF
            S3 --> TDF
            S3 --> WDF
            S3 --> EDF
            S3 --> VCF
            S3 --> GCF
            S3 --> TCF
            S3 --> WCF
            S3 --> ECF
        end
        
        subgraph "Data Catalog (Glue)"
            GC[AWS Glue Crawler]
            GD[Glue Database<br/>smartcity]
            GT_VEH[vehicle_data_table]
            GT_GPS[gps_data_table]
            GT_TRF[traffic_data_table]
            GT_WTH[weather_data_table]
            GT_EMG[emergency_data_table]
            
            GC --> GD
            GD --> GT_VEH
            GD --> GT_GPS
            GD --> GT_TRF
            GD --> GT_WTH
            GD --> GT_EMG
        end
        
        subgraph "Data Warehouse (Redshift)"
            RS[Redshift Cluster<br/>Port: 5439]
            ES_SCHEMA[External Schema]
            ET_VEH[External Table: vehicle_data]
            ET_GPS[External Table: gps_data]
            ET_TRF[External Table: traffic_data]
            ET_WTH[External Table: weather_data]
            ET_EMG[External Table: emergency_data]
            
            RS --> ES_SCHEMA
            ES_SCHEMA --> ET_VEH
            ES_SCHEMA --> ET_GPS
            ES_SCHEMA --> ET_TRF
            ES_SCHEMA --> ET_WTH
            ES_SCHEMA --> ET_EMG
        end
    end

    %% Analytics & Visualization Layer
    subgraph "Analytics & Visualization"
        DB[DBeaver<br/>SQL Client]
        DASH[Analytics Dashboard]
        REP[Reports & KPIs]
        
        DB --> DASH
        DASH --> REP
    end

    %% Container Infrastructure
    subgraph "Docker Infrastructure"
        DC[Docker Compose]
        NET[Bridge Network<br/>my_network]
        
        subgraph "Health Checks"
            ZK_HC[Zookeeper Health]
            KB_HC[Kafka Health]
            SM_HC[Spark Master Health]
        end
        
        DC --> NET
        NET --> ZK_HC
        NET --> KB_HC
        NET --> SM_HC
    end

    %% Data Flow Connections
    DG -->|Publish Messages| KB
    VT -->|Stream Read| SSJ
    GT -->|Stream Read| SSJ
    TT -->|Stream Read| SSJ
    WT -->|Stream Read| SSJ
    ET -->|Stream Read| SSJ
    
    SSJ -->|Write Parquet| S3
    S3 -->|Crawl Metadata| GC
    GD -->|External Tables| RS
    RS -->|Query Data| DB

    %% Operational Commands
    subgraph "Operations"
        MK_PROD[make kafka-producer]
        MK_SPARK[make spark-submit]
        DC_UP[docker compose up]
        DC_DOWN[docker compose down]
        
        MK_PROD -->|Start| DG
        MK_SPARK -->|Submit| SSJ
        DC_UP -->|Deploy| DC
        DC_DOWN -->|Stop| DC
    end

    %% Styling
    classDef iotSource fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef kafka fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef spark fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef aws fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef analytics fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef docker fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef operation fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class VS,GPS,TC,WS,ES,DG iotSource
    class ZK,KB,VT,GT,TT,WT,ET kafka
    class SM,SW1,SW2,SSJ,VSch,GSch,TSch,WSch,ESch,SP,WM,TR spark
    class S3,VDF,GDF,TDF,WDF,EDF,VCF,GCF,TCF,WCF,ECF,GC,GD,GT_VEH,GT_GPS,GT_TRF,GT_WTH,GT_EMG,RS,ES_SCHEMA,ET_VEH,ET_GPS,ET_TRF,ET_WTH,ET_EMG aws
    class DB,DASH,REP analytics
    class DC,NET,ZK_HC,KB_HC,SM_HC docker
    class MK_PROD,MK_SPARK,DC_UP,DC_DOWN operation
```

## Data Sources & Simulation
The project simulates 5 different IoT data streams representing smart city infrastructure:

1. Vehicle Data (vehicle_data)
    - Purpose: Track vehicle movements and characteristics
    - Fields: ID, device_id, timestamp, location, speed, direction, make, model, year, fuel_type
    - Use Case: Traffic management, vehicle tracking
2. GPS Data (gps_data)
    - Purpose: Location tracking for various vehicle types
    - Fields: ID, device_id, timestamp, speed, direction, vehicle_type
    - Use Case: Fleet management, route optimization
3. Traffic Camera Data (traffic_data)
    - Purpose: Monitor traffic conditions via cameras
    - Fields: ID, device_id, camera_id, location, timestamp, snapshot
    - Use Case: Traffic flow analysis, incident detection
4. Weather Data (weather_data)
    - Purpose: Environmental monitoring
    - Fields: ID, device_id, timestamp, location, temperature, weather_condition, precipitation, wind_speed, humidity, AQI
    - Use Case: Weather-based traffic management, environmental monitoring
5. Emergency Incident Data (emergency_data)
    - Purpose: Track emergency situations
    - Fields: ID, device_id, incident_id, type, timestamp, location, severity, status, description
    - Use Case: Emergency response, public safety

## Data Flow
The data flow is designed to simulate real-time data ingestion, processing, and storage:

```
[Data Generation] → [Kafka Topics] → [Spark Streaming] → [AWS S3] → [AWS Glue] → [AWS Redshift]
```

### Pipeline Stages:
- Data Generation (main.py)
    - Simulates vehicle journey from London to Birmingham
    - Generates realistic IoT data with timestamps
    - Publishes to respective Kafka topics

- Stream Processing (spark-city.py)
    - Consumes data from Kafka topics
    - Applies schemas and transformations
    - Implements watermarking for late data handling
    - Writes to S3 in Parquet format

- Data Lake Storage (AWS S3)
    - Organized by data type in separate folders
    - Checkpoint folders for stream processing recovery
    - Parquet format for efficient querying

- Metadata Management (AWS Glue)
    - Crawlers extract schema from Parquet files
    - Creates searchable data catalog
    - Maintains table definitions

- Analytics (AWS Redshift)
    - External tables linked to S3 data
    - SQL-based analytics and reporting
    - Connected to DBeaver for visualization


## Key Features & Capabilities
### Real-time Processing
- Structured Streaming: Processes data as it arrives
- Watermarking: Handles late-arriving data (2-minute window)
- Fault Tolerance: Checkpointing for recovery

### Scalability
- Horizontal Scaling: Multiple Spark workers
- Containerized: Easy deployment and scaling
- Cloud-native: Leverages AWS managed services

### Data Quality
- Schema Enforcement: Structured data types
- Error Handling: Delivery reports and monitoring
- Reproducibility: Seeded random generation

### Monitoring & Operations
- Spark UI: Available at localhost:9090
- Health Checks: Container-level monitoring
- Makefile Commands: Simplified operations


## Operational Commands
```
# Start infrastructure
docker compose up --build

# Generate IoT data
make kafka-producer

# Process data with Spark
make spark-submit

# Stop infrastructure
docker compose down
```

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

7. To delete topics
<img width="667" height="214" alt="image" src="https://github.com/user-attachments/assets/7e1c9e39-88a9-4047-8579-f10d73f91517" />


### Store AWS configuration keys

1. Gets AWS key from you local cli if you have set.
2. Follow this if not set (https://docs.aws.amazon.com/cli/v1/userguide/cli-authentication-user.html)
3. Use below command to get the keys from your local cli
```
aws configure export-credentials
```
4. Store them in python script like this
<img width="802" height="353" alt="image" src="https://github.com/user-attachments/assets/41de1a12-0006-4d2e-b3b5-f17a3b56b1a7" />


### Check Spark is running
1. Go to `localhost:9090` and check. It should look like this.
<img width="836" height="689" alt="image" src="https://github.com/user-attachments/assets/a3b8c16e-85eb-422f-a183-325c41ebef23" />

2. (optional) if you want to change the spark version, in the SparkSession builder, you need to change the jars as well. Go to the maven repository (https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.13/4.0.0) (Choose the version accordingly) and replace the jar configuration.

<img width="1019" height="300" alt="image" src="https://github.com/user-attachments/assets/6f8e928d-baa4-44ef-9e68-01ed8a527324" />

3. Run the code using the make file command `make spark-submit`
4. To install makefile `brew install make`


### [OPTIONAL] Create a connection in Apache Airflow (use it if you want to orchestrate the whole process)

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

### Create a AWS crawler
1. Go to AWS Glue service.
2. Click on crawler -> Create Crawler.
3. The craweler will extract the metadata information from the parquet file like column names, data types etc and make it store in a Glue Database `smartcity`
4. Fill the information like source which is S3 parquet file in the data folder, exclude pattern include `_spark_metadata` folder and choose the Glue database `smartcity` as target.
<img width="991" height="458" alt="image" src="https://github.com/user-attachments/assets/573892ec-b925-4025-9208-6054db4f4357" />

<img width="809" height="467" alt="image" src="https://github.com/user-attachments/assets/613e1133-b8da-427c-af65-8c7d05d90b4e" />

5. Check the database tables are created or not.
<img width="688" height="474" alt="image" src="https://github.com/user-attachments/assets/ea51b081-f10d-4c3b-9cd4-a5286fc6110c" />

### Create AWS Redshift and connect to local DBeaver software

#### 1. Sign In to AWS Console
- URL: https://console.aws.amazon.com/
- Login with your AWS credentials.


#### 2. Open Amazon Redshift Service
- In the AWS Console, search for **Redshift** and open it.

#### 3. Click “Create cluster”


#### 4. Choose Cluster Creation Method
- Select **“Provisioned”** for full control over nodes and resources.
- Use **“Serverless”** if you want AWS to manage compute automatically.


#### 5. Configure Cluster Details

- **Cluster Identifier**: e.g., `redshift-cluster-ritayan`
- **Database name**: e.g., `dev` (default)
- **Port**: `5439` (default)
- **Master username**: e.g., `admin`
- **Master password**: Strong password

#### 6. Choose Node Type and Cluster Size

- **Node Type**: e.g., `dc2.large`, `ra3.xlplus`
- **Cluster Type**: 
  - `single-node` for development
  - `multi-node` for production

<img width="1437" alt="image" src="https://github.com/user-attachments/assets/a3461bfe-2758-4640-b27f-ae1181d6093a" />

<img width="1282" alt="image" src="https://github.com/user-attachments/assets/82748d53-c1e8-4c06-9888-254eb2ec253a" />

#### 7. Set Network and Security

- **VPC**: Select your Virtual Private Cloud
- **Subnet Group**: Choose a Redshift subnet group
- **VPC Security Group**: Ensure port 5439 is open to your IP
- **Give Proper IAM roles**

<img width="1423" alt="image" src="https://github.com/user-attachments/assets/3ebb4bfd-ca93-47f1-a9f7-7246374847b0" />
<img width="1345" alt="image" src="https://github.com/user-attachments/assets/873ac542-8456-45a3-8ed0-8ff9b0ce9364" />


#### 8. Review and Launch
- Review all configurations
- Click **“Create cluster”**

<img width="1568" alt="image" src="https://github.com/user-attachments/assets/350a2325-406d-4489-b46b-7fb7b09a6858" />

#### 9. Connect to DBeaver
- The jdbc endpoint in the cluder information page is copied
- The username and password is used to create the connection as shown

<img width="744" height="634" alt="image" src="https://github.com/user-attachments/assets/da78b4a2-b57b-400b-ad12-e595a43cfa23" />

- Click on OK


## Results
1. First run `make kafka-producer`. It will produce the data inside the kafka topic.
<img width="876" height="289" alt="image" src="https://github.com/user-attachments/assets/64b4c8f6-30fb-45be-b6ee-9467b649adfe" />

2. Run the spark job `make spark-submit`. It will submit the spark job. It will download the required jars from the maven repository and will start the spark job.
<img width="615" height="409" alt="image" src="https://github.com/user-attachments/assets/fa24d955-6c41-4cc7-9715-dc2d88737d8a" />

3. Check AWS S3 for the files in the `data` folder
<img width="616" height="392" alt="image" src="https://github.com/user-attachments/assets/d22c1846-69da-4763-bb67-a0e74a2bb703" />
<img width="899" height="350" alt="image" src="https://github.com/user-attachments/assets/222b65ed-7510-4c3f-89ed-0463ca8d8da7" />

4. Run the crawler in the AWS Glue to reflect the latest data in the Glue Database.
5. Go to DBeaver which is connected to AWS Redshift.
6. Now connect to the Glue Database using the RedShift.
```
CREATE EXTERNAL SCHEME <GIVE_NAME>
FROM DATA CATALOG
DATABASE <glue_database_name>
IAM_ROLE <iam_role_created_to_give_reshift_access_to_glue_catelog>
REGION 'us-east-1'
```

<img width="546" height="489" alt="image" src="https://github.com/user-attachments/assets/f735d6b7-127e-4cdf-aeaf-81d701940ecd" />

<img width="584" height="307" alt="image" src="https://github.com/user-attachments/assets/2a880542-0083-4c6a-ae63-42c36d734778" />

<img width="632" height="389" alt="image" src="https://github.com/user-attachments/assets/dda6ef79-0214-4d70-bd41-abecaee8521d" />



## Use Cases and Applications

### Smart City Management
    - Traffic Optimization: Real-time traffic flow analysis
    - Emergency Response: Automated incident detection and response
    - Environmental Monitoring: Air quality and weather tracking
    - Public Transportation: Fleet management and route optimization

### Business Intelligence
    - Predictive Analytics: Traffic pattern prediction
    - Resource Planning: Emergency service allocation
    - Performance Metrics: City infrastructure KPIs
    - Historical Analysis: Trend analysis and reporting

## Potential Improvements
1. Security: Implement proper credential management (currently hardcoded)
2. Monitoring: Add comprehensive logging and alerting
3. Testing: Unit tests and integration tests
4. Spark Optimization: Fine-tune Spark configurations for performance

