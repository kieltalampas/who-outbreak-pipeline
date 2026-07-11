import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Extract
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("encoding", "UTF-8") \
    .csv("s3://bucket-name/raw/")

# Remove HXL metadata row
df = df.filter(~F.col("id_outbreak").startswith("#"))

# Drop unnecessary columns
columns_to_drop = ["icd10n", "icd103n", "icd104n", "icd10c", "icd103c", "icd104c", "iso2", "DONs"]
df = df.drop(*columns_to_drop)

# Standardize column names
df = df.toDF(*[c.lower().strip().replace(" ", "_") for c in df.columns])

# Fill nulls
df = df.fillna({
    "definition": "Unknown",
    "unsd_region": "Unknown",
    "unsd_subregion": "Unknown",
    "who_region": "Unknown"
})

# Standardize text
df = df.withColumn("country", F.initcap(F.trim(F.col("country")))) \
       .withColumn("disease", F.initcap(F.trim(F.col("disease")))) \
       .withColumn("who_region", F.initcap(F.trim(F.col("who_region")))) \
       .withColumn("unsd_region", F.initcap(F.trim(F.col("unsd_region"))))

# Cast year to integer
df = df.withColumn("year", F.col("year").cast(IntegerType()))

# Disease category
df = df.withColumn(
    "disease_category",
    F.when(F.col("disease").rlike("(?i)cholera|typhoid|hepatitis a|hepatitis e|salmonella|shigella|gastroenteritis|botulism|leptospira"), "Water-borne")
     .when(F.col("disease").rlike("(?i)ebola|marburg|lassa|haemorrhagic fever|hemorrhagic fever|rift valley|crimean"), "Hemorrhagic Fever")
     .when(F.col("disease").rlike("(?i)monkeypox|measles|smallpox|mpox"), "Viral Skin Disease")
     .when(F.col("disease").rlike("(?i)dengue|zika|yellow fever|malaria|chikungunya|west nile|onyong|encephalitis|mosquito"), "Vector-borne")
     .when(F.col("disease").rlike("(?i)covid|influenza|sars|mers|respiratory|pneumonia|bronchitis|syncytial"), "Respiratory")
     .when(F.col("disease").rlike("(?i)meningitis|meningococcal|polio|rabies|plague|anthrax"), "Bacterial/Neurological")
     .otherwise("Other")
)

# Year bucket
df = df.withColumn(
    "year_bucket",
    F.when(F.col("year") <= 2000, "1996-2000")
     .when((F.col("year") > 2000) & (F.col("year") <= 2005), "2001-2005")
     .when((F.col("year") > 2005) & (F.col("year") <= 2010), "2006-2010")
     .when((F.col("year") > 2010) & (F.col("year") <= 2015), "2011-2015")
     .when((F.col("year") > 2015) & (F.col("year") <= 2020), "2016-2020")
     .otherwise("2021-Present")
)

# Severity flag
df = df.withColumn(
    "outbreak_severity",
    F.when(F.col("disease").rlike("(?i)ebola|marburg|lassa|monkeypox"), "High")
     .when(F.col("disease").rlike("(?i)cholera|dengue|yellow fever|measles"), "Medium")
     .otherwise("Low")
)

# Write to S3 processed
df.write \
  .mode("overwrite") \
  .parquet("s3://bucket-name/processed/")

job.commit()