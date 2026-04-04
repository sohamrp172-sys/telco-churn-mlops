@echo off
title Telco Churn MLOps - Auto Deploy
color 0A

echo.
echo ============================================================
echo   TELCO CHURN MLOPS - AUTO DEPLOYMENT SCRIPT
echo ============================================================
echo.

:: ---- STEP 1: FIX NUMPY INCOMPATIBILITY ----
echo [STEP 1/5] Fixing package compatibility issues...
echo.
pip uninstall numpy pandas mlflow scikit-learn -y >nul 2>&1
echo   Removed old conflicting packages.

echo   Installing correct compatible versions (this may take 2-5 mins)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo   ERROR: Failed to install requirements!
    echo   Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.
echo [OK] All packages installed successfully!
echo.

:: ---- STEP 2: CHECK / GENERATE RAW DATA ----
echo [STEP 2/5] Checking for raw data file...
echo.
if not exist "data\raw\telco_v1.csv" (
    echo   Data file not found. Generating realistic dataset automatically...
    python generate_data.py
    if %errorlevel% neq 0 (
        echo.
        echo   ERROR: Could not generate data. Check the error above.
        pause
        exit /b 1
    )
) else (
    echo [OK] Data file found at data\raw\telco_v1.csv
)

:: ---- STEP 3: PREPROCESS DATA ----
echo.
echo [STEP 3/5] Preprocessing the data...
echo.
python src\preprocess.py --input data\raw\telco_v1.csv --output data\processed\telco_processed.csv
if %errorlevel% neq 0 (
    echo.
    echo   ERROR: Preprocessing failed! Check the error above.
    pause
    exit /b 1
)
echo [OK] Data preprocessed and saved!

:: ---- STEP 4: TRAIN THE ML MODEL ----
echo.
echo [STEP 4/5] Training the Machine Learning model...
echo.
python src\train.py --input data\processed\telco_processed.csv --model-type gb --run-name v4-gb-deterministic
if %errorlevel% neq 0 (
    echo.
    echo   ERROR: Training failed! Check the error above.
    pause
    exit /b 1
)
echo [OK] Model trained and saved to models\churn_model.pkl

:: ---- STEP 5: START THE SERVER ----
echo.
echo [STEP 5/5] Starting the API server...
echo.
echo ============================================================
echo.
echo   SUCCESS! Your project is now LIVE!
echo.
echo   Open your browser and go to:
echo   http://localhost:8000          (Dashboard)
echo   http://localhost:8000/docs     (API Docs)
echo   http://localhost:8000/health   (Health Check)
echo.
echo   Press CTRL+C to stop the server when you are done.
echo.
echo ============================================================
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
