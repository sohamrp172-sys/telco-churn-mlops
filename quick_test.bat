@echo off
echo Testing if model is loaded correctly...
echo.

python -c "import joblib; import os; path='models/churn_model.pkl'; print('Model file exists:', os.path.exists(path)); model=joblib.load(path) if os.path.exists(path) else None; print('Model type:', type(model).__name__ if model else 'None'); print('Features:', len(model.feature_names_in_) if model and hasattr(model, 'feature_names_in_') else 0)"

echo.
echo If you see "GradientBoostingClassifier" above, your model is correct!
echo.
pause
