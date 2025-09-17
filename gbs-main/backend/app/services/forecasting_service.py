from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder


def generate_mock_historical_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    trials = [101, 102, 103, 104, 105]
    years = [2022, 2023, 2024]
    quarters = [1, 2, 3, 4]
    skill_types = [
        "Biostatistician",
        "Clinical Research Associate",
        "Data Manager",
        "Project Manager",
    ]

    rows: List[Dict] = []
    for trial_id in trials:
        for year in years:
            for quarter in quarters:
                # Simulate higher demand as we move to Phase 3 patterns
                base = 5 + (year - years[0]) * 1.2 + quarter * 0.8
                for skill in skill_types:
                    skill_factor = {
                        "Biostatistician": 1.4,
                        "Clinical Research Associate": 1.8,
                        "Data Manager": 1.2,
                        "Project Manager": 1.0,
                    }[skill]
                    noise = rng.normal(0, 0.8)
                    units = max(0.5, base * skill_factor + noise)
                    rows.append(
                        {
                            "trial_id": trial_id,
                            "phase": 3,  # historical data skewed towards phase 3 workloads
                            "quarter": quarter,
                            "year": year,
                            "skill_type": skill,
                            "units_demanded": round(units, 2),
                        }
                    )
    return pd.DataFrame(rows)


def train_phase3_forecast_model() -> Tuple[LinearRegression, OneHotEncoder, List[str]]:
    df = generate_mock_historical_data()

    # Feature engineering
    X_num = df[["quarter", "year", "phase"]].to_numpy()
    enc = OneHotEncoder(sparse_output=False)
    X_cat = enc.fit_transform(df[["skill_type"]])
    X = np.hstack([X_num, X_cat])
    y = df["units_demanded"].to_numpy()

    model = LinearRegression()
    model.fit(X, y)

    skill_categories = list(enc.categories_[0])
    return model, enc, skill_categories


def predict_phase3_next_four_quarters(model: LinearRegression, enc: OneHotEncoder, start_year: int, start_quarter: int, skill_types: List[str]) -> List[Dict]:
    results: List[Dict] = []

    year = start_year
    quarter = start_quarter
    for i in range(4):
        for skill in skill_types:
            X_num = np.array([[quarter, year, 3]])
            X_cat = enc.transform([[skill]])
            X = np.hstack([X_num, X_cat])
            pred = float(model.predict(X)[0])
            results.append(
                {
                    "year": year,
                    "quarter": quarter,
                    "skill_type": skill,
                    "units_demanded": round(max(0.0, pred), 2),
                }
            )

        # advance quarter
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1

    return results


