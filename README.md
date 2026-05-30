# Auto MPG ML Monorepo

Production-ready monorepo for the Auto MPG project with a FastAPI backend and a static HTML, CSS, JavaScript frontend.

## Structure

- `frontend/` - automobile-themed dashboard UI
- `backend/` - FastAPI service and model runtime
- `api/` - Vercel Python entrypoint that exposes the FastAPI app
- `notebooks/` - project notebooks
- `data/` - raw dataset

## API

- `POST /api/predict`
- `GET /api/health`

### Request body

```json
{
  "car_name": "ford torino",
  "cylinders": 8,
  "displacement": 307,
  "horsepower": 130,
  "weight": 3504,
  "acceleration": 12,
  "model_year": 70,
  "origin": 1
}
```

### Response body

```json
{
  "predicted_mpg": 18.4,
  "efficiency_band": "Performance",
  "brand": "ford",
  "performance_metrics": {
    "horsepower_to_weight": 0.037,
    "weight_per_horsepower": 26.954,
    "acceleration": 12
  }
}
```

## Local development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn backend.app.main:app --reload
```

Open `frontend/index.html` through a static file server or deploy the repository to Vercel.

## Vercel deployment

The repository is deployment-ready as-is.

- Static frontend is served from `frontend/`
- FastAPI is exposed through `api/index.py`
- Frontend calls the backend with `/api/predict`

## Model notes

- The trained model is stored at `backend/app/models/model.pkl`
- The pipeline was trained from the notebook in `notebooks/EDA_and_Preprocessing.ipynb`
- The original notebook reported a pipeline R2 score of about `0.907`
