# !/bin/sh
# echo "Waiting for MinIO to start..."

# until curl -s http://localhost:9000/minio/health/live; do
#     echo "MinIO not ready yet, waiting..."
#     sleep 5
# done

sleep 5

mc alias set minioserver http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create the mlflow bucket
mc mb minioserver/mlflow-artifacts
