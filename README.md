# Moving Average Suppression Analysis System

This system analyzes the relationship between stock prices and moving averages, identifying the moving average that most frequently suppresses the stock price for each stock.

## Project Structure

- `backend/`: FastAPI backend application
  - `app/`: Main application code
    - `data/`: Data acquisition and storage
    - `analysis/`: Suppression rules and analysis
    - `api/`: API endpoints
- `frontend/`: React frontend application
  - `src/`: Source code
    - `components/`: React components
    - `utils/`: Utility functions
    - `pages/`: Page components
