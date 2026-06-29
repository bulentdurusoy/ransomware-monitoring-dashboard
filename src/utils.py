"""
Ransomware Monitoring Dashboard - Utility Functions
Helper functions for data loading, validation, cleaning, filtering, and IOC search.
"""

import os
import pandas as pd

# ── Required columns that every uploaded dataset must contain ───────────────────
REQUIRED_COLUMNS = [
    "date",
    "ransomware_group",
    "country",
    "target_sector",
    "attack_vector",
    "technique",
    "severity",
    "ioc_ip",
    "ioc_hash",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  FILE I/O
# ═══════════════════════════════════════════════════════════════════════════════

def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Read an uploaded file (CSV or XLSX) into a DataFrame.
    Raises ValueError on unsupported format.
    """
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {name}. Please upload a .csv or .xlsx file.")


def load_file_from_path(file_path: str) -> pd.DataFrame:
    """
    Read a CSV or XLSX file from a local filesystem path.
    Raises ValueError on unsupported format.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def scan_data_directory(data_dir: str = "/app/data") -> list[str]:
    """
    Scan the given directory for CSV/XLSX files and return a list of filenames.
    Returns an empty list if the directory does not exist or is empty.
    """
    if not os.path.isdir(data_dir):
        return []
    valid_extensions = (".csv", ".xlsx", ".xls")
    return sorted(
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f)) and f.lower().endswith(valid_extensions)
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_columns(df: pd.DataFrame) -> list[str]:
    """
    Check that all REQUIRED_COLUMNS exist in the DataFrame.
    Returns a list of missing column names (empty list = all OK).
    """
    present = set(c.strip().lower() for c in df.columns)
    missing = [col for col in REQUIRED_COLUMNS if col.lower() not in present]
    return missing


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip whitespace and lower-case the column names so that validation
    is case-insensitive, then map back to the expected canonical names.
    """
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA CLEANING
# ═══════════════════════════════════════════════════════════════════════════════

def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Clean and sanitize the uploaded dataset.

    Returns
    -------
    (cleaned_df, warnings)
        cleaned_df : DataFrame ready for analytics.
        warnings   : list of human-readable warning strings about dropped/fixed rows.
    """
    warnings: list[str] = []
    original_len = len(df)

    # --- Normalize column names ---
    df = normalize_column_names(df.copy())

    # --- Fill text NaN values ---
    text_cols = ["ransomware_group", "country", "target_sector", "attack_vector", "technique"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    df["ioc_ip"] = df["ioc_ip"].fillna("") if "ioc_ip" in df.columns else ""
    df["ioc_hash"] = df["ioc_hash"].fillna("") if "ioc_hash" in df.columns else ""

    # --- Parse date column ---
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        invalid_dates = df["date"].isna().sum()
        if invalid_dates > 0:
            warnings.append(f"{invalid_dates} row(s) with invalid/missing dates were removed.")
            df = df.dropna(subset=["date"])

    # --- Parse severity column ---
    if "severity" in df.columns:
        df["severity"] = pd.to_numeric(df["severity"], errors="coerce")
        invalid_sev = df["severity"].isna().sum()
        if invalid_sev > 0:
            warnings.append(f"{invalid_sev} row(s) with non-numeric severity were removed.")
            df = df.dropna(subset=["severity"])

        df["severity"] = df["severity"].astype(int)

        # Enforce 1–10 range
        out_of_range = ((df["severity"] < 1) | (df["severity"] > 10)).sum()
        if out_of_range > 0:
            warnings.append(
                f"{out_of_range} row(s) with severity outside the 1-10 range were excluded."
            )
            df = df[(df["severity"] >= 1) & (df["severity"] <= 10)]

    # --- Summary ---
    dropped = original_len - len(df)
    if dropped > 0:
        warnings.append(f"Total rows removed during cleaning: {dropped} / {original_len}.")

    df = df.reset_index(drop=True)
    return df, warnings


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_summary(df: pd.DataFrame) -> dict:
    """
    Return a dict of high-level summary statistics for the dashboard cards.
    """
    if df.empty:
        return {
            "total_attacks": 0,
            "unique_groups": 0,
            "top_country": "N/A",
            "top_sector": "N/A",
            "avg_severity": 0.0,
            "max_severity": 0,
        }

    return {
        "total_attacks": len(df),
        "unique_groups": df["ransomware_group"].nunique(),
        "top_country": df["country"].value_counts().idxmax(),
        "top_sector": df["target_sector"].value_counts().idxmax(),
        "avg_severity": round(df["severity"].mean(), 2),
        "max_severity": int(df["severity"].max()),
    }


def search_ioc(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search for an IOC value (IP or hash) across the ioc_ip and ioc_hash columns.
    Returns matching rows.
    """
    query = query.strip()
    if not query:
        return pd.DataFrame()

    mask = (
        df["ioc_ip"].astype(str).str.contains(query, case=False, na=False)
        | df["ioc_hash"].astype(str).str.contains(query, case=False, na=False)
    )
    return df.loc[mask]


def filter_dataframe(
    df: pd.DataFrame,
    date_range: tuple = None,
    groups: list = None,
    countries: list = None,
    sectors: list = None,
    severity_range: tuple = None,
) -> pd.DataFrame:
    """
    Apply sidebar filters to the DataFrame and return the filtered result.
    """
    filtered = df.copy()

    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

    if groups:
        filtered = filtered[filtered["ransomware_group"].isin(groups)]

    if countries:
        filtered = filtered[filtered["country"].isin(countries)]

    if sectors:
        filtered = filtered[filtered["target_sector"].isin(sectors)]

    if severity_range and len(severity_range) == 2:
        lo, hi = severity_range
        filtered = filtered[(filtered["severity"] >= lo) & (filtered["severity"] <= hi)]

    return filtered
