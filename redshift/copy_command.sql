COPY outbreak_schema.disease_outbreaks
FROM 's3://who-outbreaks-pipeline-kiel/processed/'
IAM_ROLE 'arn:aws:iam::XXXXXXXXXXXX:role/redshift-s3-role'
FORMAT AS PARQUET;