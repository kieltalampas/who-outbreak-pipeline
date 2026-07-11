CREATE TABLE outbreak_schema.disease_outbreaks (
    id_outbreak       VARCHAR(50),
    year              INTEGER,
    disease           VARCHAR(100),
    definition        VARCHAR(5000),
    country           VARCHAR(100),
    iso3              VARCHAR(10),
    unsd_region       VARCHAR(100),
    unsd_subregion    VARCHAR(100),
    who_region        VARCHAR(100),
    disease_category  VARCHAR(50),
    year_bucket       VARCHAR(20),
    outbreak_severity VARCHAR(10)
);