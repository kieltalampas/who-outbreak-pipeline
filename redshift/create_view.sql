CREATE VIEW outbreak_schema.vw_outbreak_summary AS
SELECT
    year, year_bucket, disease, disease_category,
    outbreak_severity, country, iso3,
    unsd_region, unsd_subregion, who_region,
    COUNT(*) as outbreak_count
FROM outbreak_schema.disease_outbreaks
GROUP BY
    year, year_bucket, disease, disease_category,
    outbreak_severity, country, iso3,
    unsd_region, unsd_subregion, who_region;