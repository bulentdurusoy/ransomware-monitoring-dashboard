"""
Ransomware Monitoring Dashboard - Data Generator
Generates a simulated but realistic ransomware incident dataset.
"""

import os
import random
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ─── Realistic Sample Values ───────────────────────────────────────────────────

RANSOMWARE_GROUPS = [
    "LockBit", "BlackCat", "Cl0p", "Conti", "Akira",
    "Black Basta", "Royal", "Hive", "Medusa", "Play",
]

# Weighted probabilities – LockBit and BlackCat are historically more prolific
GROUP_WEIGHTS = [0.18, 0.14, 0.12, 0.10, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06]

COUNTRIES = [
    "USA", "Germany", "France", "UK", "Turkey",
    "Canada", "Japan", "India", "Brazil", "Netherlands", "Australia",
]

COUNTRY_WEIGHTS = [0.22, 0.12, 0.10, 0.10, 0.08, 0.07, 0.07, 0.06, 0.06, 0.06, 0.06]

SECTORS = [
    "Healthcare", "Finance", "Education", "Government",
    "Manufacturing", "Energy", "Retail", "Technology", "Transportation",
]

ATTACK_VECTORS = [
    "Phishing", "RDP Brute Force", "Exploited Vulnerability",
    "Malicious Attachment", "Credential Theft", "Supply Chain", "VPN Exploit",
]

MITRE_TECHNIQUES = [
    "T1486 - Data Encrypted for Impact",
    "T1059 - Command and Scripting Interpreter",
    "T1078 - Valid Accounts",
    "T1566 - Phishing",
    "T1190 - Exploit Public-Facing Application",
    "T1021 - Remote Services",
    "T1041 - Exfiltration Over C2 Channel",
]

# ─── Helper Functions ──────────────────────────────────────────────────────────

def generate_random_ip() -> str:
    """Generate a random public-looking IP address (avoids reserved ranges)."""
    while True:
        octets = [random.randint(1, 254) for _ in range(4)]
        # Skip common private ranges
        if octets[0] in (10, 127):
            continue
        if octets[0] == 172 and 16 <= octets[1] <= 31:
            continue
        if octets[0] == 192 and octets[1] == 168:
            continue
        return ".".join(str(o) for o in octets)


def generate_sha256_hash() -> str:
    """Generate a realistic-looking SHA256 hash (64 hex characters)."""
    seed = f"{random.random()}-{datetime.now().timestamp()}-{random.randint(0, 10**9)}"
    return hashlib.sha256(seed.encode()).hexdigest()


def generate_random_date(start: datetime, end: datetime) -> str:
    """Return a random date between *start* and *end* (inclusive) as YYYY-MM-DD."""
    delta = (end - start).days
    random_days = random.randint(0, delta)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")


# ─── Main Generator ───────────────────────────────────────────────────────────

def generate_dataset(num_records: int = 150, output_path: str = None) -> pd.DataFrame:
    """
    Generate a simulated ransomware incident dataset.

    Parameters
    ----------
    num_records : int
        Number of incident records to generate (default: 150).
    output_path : str or None
        If provided, save the resulting DataFrame as a CSV to this path.

    Returns
    -------
    pd.DataFrame
        The generated dataset.
    """
    random.seed(42)
    np.random.seed(42)

    # Date range: 2025-01-01 → 2026-12-31
    date_start = datetime(2025, 1, 1)
    date_end = datetime(2026, 12, 31)

    records = []
    for _ in range(num_records):
        record = {
            "date": generate_random_date(date_start, date_end),
            "ransomware_group": random.choices(RANSOMWARE_GROUPS, weights=GROUP_WEIGHTS, k=1)[0],
            "country": random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0],
            "target_sector": random.choice(SECTORS),
            "attack_vector": random.choice(ATTACK_VECTORS),
            "technique": random.choice(MITRE_TECHNIQUES),
            "severity": random.randint(1, 10),
            "ioc_ip": generate_random_ip(),
            "ioc_hash": generate_sha256_hash(),
        }
        records.append(record)

    df = pd.DataFrame(records)
    # Sort by date for cleaner analysis
    df = df.sort_values("date").reset_index(drop=True)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"[OK] Dataset generated: {output_path}  ({len(df)} records)")

    return df


# Allow standalone execution
if __name__ == "__main__":
    generate_dataset(
        num_records=150,
        output_path=os.path.join(os.path.dirname(__file__), "..", "data", "ransomware_dataset.csv"),
    )
