"""
Verification script to test if local and Render predictions match
"""
import requests
import json

# Test data - same customer profile
test_customer = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": "844.2"
}

def test_endpoint(base_url, name):
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        health_data = health_response.json()
        print(f"\n✓ Health Check:")
        print(f"  Status: {health_data.get('status')}")
        print(f"  Model Loaded: {health_data.get('model_loaded')}")
        print(f"  Model Type: {health_data.get('model_type')}")
        print(f"  Is Dummy: {health_data.get('is_dummy')}")
        print(f"  Features: {health_data.get('feature_count')}")
        
        if health_data.get('is_dummy'):
            print(f"\n⚠️  WARNING: Using DUMMY model (not real trained model)!")
        else:
            print(f"\n✓ Using REAL trained model")
            
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return None
    
    # Test prediction
    try:
        pred_response = requests.post(
            f"{base_url}/predict",
            json=test_customer,
            timeout=10
        )
        pred_data = pred_response.json()
        print(f"\n✓ Prediction Result:")
        print(f"  Churn Prediction: {pred_data.get('churn_prediction')}")
        print(f"  Churn Probability: {pred_data.get('churn_probability'):.4f}")
        
        return pred_data
        
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DEPLOYMENT VERIFICATION TOOL")
    print("="*60)
    
    # Test local
    local_result = test_endpoint("http://localhost:8000", "LOCAL")
    
    # Test Render (update with your actual Render URL)
    render_url = input("\n\nEnter your Render URL (or press Enter to skip): ").strip()
    
    if render_url:
        render_result = test_endpoint(render_url, "RENDER")
        
        # Compare results
        if local_result and render_result:
            print(f"\n{'='*60}")
            print("COMPARISON")
            print(f"{'='*60}")
            
            local_prob = local_result.get('churn_probability')
            render_prob = render_result.get('churn_probability')
            
            if abs(local_prob - render_prob) < 0.01:
                print("✓ PREDICTIONS MATCH! Both environments are using the same model.")
            else:
                print("✗ PREDICTIONS DIFFER!")
                print(f"  Local:  {local_prob:.4f}")
                print(f"  Render: {render_prob:.4f}")
                print(f"  Difference: {abs(local_prob - render_prob):.4f}")
                print("\n  This means Render is likely using the dummy model.")
    
    print("\n" + "="*60)
