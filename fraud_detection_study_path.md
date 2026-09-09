# Developer Study Path: Fraud Detection Data Pipeline

**Proposal for CEO review and subsequent sharing with the development team**

## Objective

Prepare our PHP developers to build a reliable pipeline from a client database into our own database, then prepare transaction-level data for fraud modelling. Their existing backend experience provides a foundation for database integration, validation, and error handling.

Client data is not yet available, and its structure is unknown. Learning will therefore use a mock project; the final schema, fraud definition, and model approach will be decided after reviewing client data.

## Learning Path

Complete the stages in order, combining focused study with a working deliverable at each stage.

| Stage | Study focus | Practical deliverable |
|---|---|---|
| **1. Python foundations** | Python syntax, collections, functions, modules, virtual environments, exceptions, logging, and database connections. | A Python script that reads records from a mock client database and writes them into a separate destination database. |
| **2. SQL and data exploration** | Joins, aggregations, window functions, indexes, and pandas for inspecting data. | A data-quality report identifying missing values, duplicates, unmatched chargebacks, and transaction counts by date. |
| **3. Reliable pipelines** | Initial and incremental loads, upserts, batching, checkpoints, retries, schema changes, and secure credential handling. | A repeatable pipeline that handles updates and resumes after failure without losing or duplicating records; verify source and destination totals. |
| **4. Transaction-level data preparation** | Table relationships, one row per transaction, historical features, outcome labels, and prevention of data leakage. | A training dataset containing transaction details, prior customer activity, and a clearly defined outcome label. |
| **5. Basic fraud modelling** | Classification, logistic regression, tree models, class imbalance, precision, recall, thresholds, and time-based evaluation. | A baseline model trained on older transactions and tested on newer ones, reporting false positives and missed fraud. |

## Practice Before Client Access

Use one project throughout: mock **customers, transactions, and chargebacks** in a source database, feeding a separate destination database. Introduce missing fields, duplicates, changed records, late chargebacks, and new columns to test reliability. Synthetic data supports engineering practice; it does not establish real fraud-detection performance.

Two rules apply to data preparation: **a chargeback is not automatically fraud**, and **features must contain only information available when the transaction would be scored**. Agree on fraud labels and the time needed to observe outcomes once client data becomes available.

## Working Approach and Readiness

Both developers should complete stages 1–3. They can then divide responsibility between pipeline reliability and data preparation/modelling while reviewing each other's work. Review progress through a short weekly demonstration; advance when each deliverable works and the developer can explain and troubleshoot it.

The immediate readiness milestone is a reliable mock pipeline and a documented transaction-level dataset. When client access arrives, first inspect the schema, relationships, data quality, and available history, then adapt the pipeline and confirm whether the data supports the intended model.
