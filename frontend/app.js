document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // UI Elements
    const btn = document.getElementById('predict-btn');
    const btnText = document.getElementById('btn-text');
    const loader = document.getElementById('btn-loader');
    const resultEmpty = document.getElementById('result-container');
    const resultData = document.getElementById('result-data');
    const gaugeFill = document.getElementById('gauge-fill');
    const probPercentage = document.getElementById('prob-percentage');
    const churnStatus = document.getElementById('churn-status');
    const statusCard = document.getElementById('status-card');
    
    // Set Loading State
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    btn.disabled = true;

    // Collect Data
    const formData = new FormData(e.target);
    const data = {};
    formData.forEach((value, key) => {
        // Coerce numbers for schema if needed
        if (key === 'SeniorCitizen' || key === 'tenure') {
            data[key] = parseInt(value, 10);
        } else if (key === 'MonthlyCharges') {
            data[key] = parseFloat(value);
        } else {
            data[key] = value;
        }
    });

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        
        // Hide empty state, show data state
        resultEmpty.classList.add('hidden');
        resultData.classList.remove('hidden');

        // Animate Result
        const probability = Math.round(result.churn_probability * 100);
        
        // Update Gauge (Path length is ~125.6, offset represents empty portion)
        // 125.6 * (1 - probability/100)
        const circumference = 125.6;
        const offset = circumference - (probability / 100) * circumference;
        
        // Short delay to allow display:block to render before transitioning offset
        setTimeout(() => {
            gaugeFill.style.strokeDashoffset = offset;
        }, 50);

        // Update Text
        probPercentage.innerText = `${probability}%`;
        
        if (result.churn_prediction === 1 || probability >= 50) {
            // High Churn Risk
            gaugeFill.style.stroke = 'var(--danger)';
            churnStatus.innerText = 'High Risk';
            churnStatus.style.color = 'var(--danger)';
            statusCard.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        } else {
            // Low Churn Risk
            gaugeFill.style.stroke = 'var(--safe)';
            churnStatus.innerText = 'Low Risk';
            churnStatus.style.color = 'var(--safe)';
            statusCard.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        }

    } catch (err) {
        console.error(err);
        alert(`Failed to fetch prediction: ${err.message}. Make sure the API is running.`);
    } finally {
        // Reset UI Button
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
        btn.disabled = false;
    }
});
