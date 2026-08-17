# Cloud Data Engineering Pipeline

A production-style batch data engineering pipeline built with Python, Pandas, PyArrow, DuckDB, automated data-quality validation, incremental loading, retry handling, observability, structured logging, Docker, and GitHub Actions CI/CD.

The project demonstrates how a real-world data pipeline can be designed to be reliable, testable, observable, and reproducible without depending on cloud infrastructure.

---

## 1. Project Overview

This project ingests post and user data from REST APIs, processes the data through multiple pipeline layers, validates data quality and relationships, performs incremental loading, creates an analytics-ready dataset, and records operational information such as audits, metrics, retries, alerts, and logs.

The complete pipeline contains 9 stages:

1. Post ingestion
2. User ingestion
3. Post transformation
4. User transformation
5. Post validation
6. Relationship validation
7. Schema validation
8. Incremental load
9. Analytics dataset creation

The pipeline is executed sequentially and stops when a non-recoverable stage fails.

---

## 2. Architecture

```text
                         REST APIs
                            |
             +--------------+--------------+
             |                             |
             v                             v
      Post Ingestion                 User Ingestion
             |                             |
             v                             v
        data/raw/                      data/raw/
             |                             |
             v                             v
    Post Transformation          User Transformation
             |                             |
             v                             v
      data/staging/                 data/curated/
             |
             v
      Data Quality
       Validation
             |
             v
    Relationship Validation
             |
             v
      Schema Validation
             |
             v
     Incremental Upsert
             |
             v
       Curated Posts
             |
             +------------------+
             |                  |
             v                  v
      Analytics Dataset    Audit / Metrics
             |                  |
             v                  v
       Parquet Output       Logs / Alerts
