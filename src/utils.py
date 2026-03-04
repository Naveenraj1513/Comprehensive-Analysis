import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def save_plot(plt_obj, output_dir, filename):
    create_dir(output_dir)
    path = os.path.join(output_dir, filename)
    plt_obj.tight_layout()
    plt_obj.savefig(path, dpi=150)
    print(f"📊 Saved plot: {path}")

def handle_missing_values(df):
    df.replace(['NA', 'N/A', 'na', 'n/a', 'None', '', 'null'], np.nan, inplace=True)
    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    for c in num_cols:
        if df[c].isnull().sum() > 0:
            df[c].fillna(df[c].median(), inplace=True)
    for c in cat_cols:
        if df[c].isnull().sum() > 0:
            df[c].fillna(df[c].mode()[0] if not df[c].mode().empty else "Unknown", inplace=True)
    return df

def find_column(df, keywords):
    cols_lower = [c.lower() for c in df.columns]
    for kw in keywords:
        for i, c in enumerate(cols_lower):
            if kw.lower() in c:
                return df.columns[i]
    return None