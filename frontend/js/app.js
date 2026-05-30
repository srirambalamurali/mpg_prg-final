const form = document.getElementById('prediction-form');
const mpgValue = document.getElementById('mpg-value');
const efficiencyBand = document.getElementById('efficiency-band');
const hpWeight = document.getElementById('hp-weight');
const weightHp = document.getElementById('weight-hp');
const brandToken = document.getElementById('brand-token');
const performanceBias = document.getElementById('performance-bias');
const originProfile = document.getElementById('origin-profile');
const statusMessage = document.getElementById('status-message');

function bandLabel(mpg) {
  if (mpg >= 30) return 'Efficient street cruiser';
  if (mpg >= 22) return 'Balanced everyday driver';
  return 'Performance-oriented machine';
}

function originLabel(origin) {
  if (origin === 2) return 'European market profile';
  if (origin === 3) return 'Japanese market profile';
  return 'Domestic baseline';
}

function readFormValue(name) {
  return form.elements[name].value;
}

async function submitPrediction(event) {
  event.preventDefault();
  statusMessage.textContent = 'Running inference against the FastAPI model...';

  const payload = {
    car_name: readFormValue('car_name'),
    cylinders: Number(readFormValue('cylinders')),
    displacement: Number(readFormValue('displacement')),
    horsepower: Number(readFormValue('horsepower')),
    weight: Number(readFormValue('weight')),
    acceleration: Number(readFormValue('acceleration')),
    model_year: Number(readFormValue('model_year')),
    origin: Number(readFormValue('origin')),
  };

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || 'Prediction request failed.');
    }

    const result = await response.json();
    const mpg = Number(result.predicted_mpg);
    const metrics = result.performance_metrics || {};

    mpgValue.textContent = `${mpg.toFixed(1)} MPG`;
    efficiencyBand.textContent = result.efficiency_band || bandLabel(mpg);
    hpWeight.textContent = `${Number(metrics.horsepower_to_weight || 0).toFixed(4)}`;
    weightHp.textContent = `${Number(metrics.weight_per_horsepower || 0).toFixed(2)}`;
    brandToken.textContent = result.brand || payload.car_name.split(' ')[0].toLowerCase();
    performanceBias.textContent = bandLabel(mpg);
    originProfile.textContent = originLabel(payload.origin);
    statusMessage.textContent = 'Prediction completed successfully.';
  } catch (error) {
    mpgValue.textContent = '--';
    efficiencyBand.textContent = 'Unable to score vehicle';
    statusMessage.textContent = error.message;
  }
}

form.addEventListener('submit', submitPrediction);

form.addEventListener('reset', () => {
  window.requestAnimationFrame(() => {
    mpgValue.textContent = '--';
    efficiencyBand.textContent = 'Awaiting prediction';
    hpWeight.textContent = '--';
    weightHp.textContent = '--';
    brandToken.textContent = '--';
    performanceBias.textContent = 'Classic cruiser profile';
    originProfile.textContent = 'Domestic baseline';
    statusMessage.textContent = 'Submit the form to generate an MPG prediction.';
  });
});
