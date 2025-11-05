#!/bin/bash
# Start Label Studio with Auto ML Backend Connection

# Set environment variables for auto ML backend connection
export ADD_DEFAULT_ML_BACKENDS=true
export DEFAULT_ML_BACKEND_URL=http://localhost:9090
export DEFAULT_ML_BACKEND_TITLE="SAM Model"

echo "Environment variables set:"
echo "  ADD_DEFAULT_ML_BACKENDS=$ADD_DEFAULT_ML_BACKENDS"
echo "  DEFAULT_ML_BACKEND_URL=$DEFAULT_ML_BACKEND_URL"
echo "  DEFAULT_ML_BACKEND_TITLE=$DEFAULT_ML_BACKEND_TITLE"
echo ""
echo "Starting Label Studio..."
echo "New projects will automatically connect to ML backend at $DEFAULT_ML_BACKEND_URL"
echo ""

cd label_studio
python3 manage.py runserver 0.0.0.0:8080
