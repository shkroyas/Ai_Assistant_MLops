# Service catalog — example company handbook
The assistant backend exposes POST /ask and POST /batch. The churn API exposes POST /predict with churn probability and model version. The assistant UI runs on port 8501; assistant API on port 8000; churn API on port 8001; MLflow on port 5000. Cached answers expire after 300 seconds and are invalidated by a corpus or configuration change.
