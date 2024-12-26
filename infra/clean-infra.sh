if [ -f ".env" ]; then
    source .env
fi

postgres_data="${POSTGRES_CONTAINER}_data"
minio_data="${MINIO_CONTAINER}_data"

sudo rm -rf $postgres_data

sudo rm -rf $minio_data