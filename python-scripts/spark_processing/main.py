import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast


spark = SparkSession.builder \
    .appName("flights-analysis") \
    .getOrCreate()

df_flights = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://pg-flights-data:5432/postgres") \
    .option("dbtable", "flights") \
    .option("user", "postgres") \
    .option("password", "postgres") \
    .option("driver", "org.postgresql.Driver") \
    .option("numPartitions", 31) \
    .option("partitionColumn", "day") \
    .option("lowerBound", 0)\
    .option("upperBound", 31)\
    .load()

print(f"Partition count:{df_flights.rdd.getNumPartitions()}")

df_airlines = spark.read\
                .options(delimeter=',', inferSchema='True', header='True') \
                .csv("s3a://airport-data/airlines.csv")
df_airports = spark.read\
                .options(delimiter=',', inferSchema='True', header='True') \
                .csv("s3a://airport-data/airports.csv")

from pyspark.sql.functions import col

df_airlines = df_airlines.select([col(c).alias("AL_"+c) for c in df_airlines.columns])
df_o_airports = df_airports.select([col(c).alias("ORIG_"+c) for c in df_airports.columns])
df_d_airports = df_airports.select([col(c).alias("DEST_"+c) for c in df_airports.columns])

df_flights = df_flights\
    .join(broadcast(df_airlines), df_flights.airline == df_airlines.AL_IATA_CODE)\
    .join(broadcast(df_o_airports), df_flights.origin_airport == df_o_airports.ORIG_IATA_CODE)\
    .join(broadcast(df_d_airports), df_flights.destination_airport == df_d_airports.DEST_IATA_CODE)

#df_flights.printSchema()

output_location = "s3a://flights-data/flights"

df_flights.cache() #this is to make sure the DAG is not recalculated when we call the .count() later
df_flights.write.mode("overwrite")\
    .option("header","true")\
    .format("parquet").save(output_location)