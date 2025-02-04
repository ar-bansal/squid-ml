if [ -f ".env" ]; then
    source .env
fi

sudo rm -rf "../../mlops_data"