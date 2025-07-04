# Gym Progress Tracker

This Streamlit application tracks weightlifting progress using CSV files. It loads training logs, merges them with user and machine information and visualizes progress with Altair charts.

## Setup

Install dependencies with:

```bash
pip install -r requirements.txt
```

Run the app with:

```bash
streamlit run main.py
```

The CSV files inside `data/` store muscle groups, users and progress logs. New records are appended to `data/Progreso.csv` when they are saved through the app.

Unit tests can be executed with:

```bash
pytest
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
