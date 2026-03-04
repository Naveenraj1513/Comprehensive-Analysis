import os
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from config import DEFAULT_FILE, OUTPUT_DIR, FIG_SIZE, STYLE
from utils import save_plot, handle_missing_values, find_column

sns.set_style(STYLE)
plt.rcParams['figure.figsize'] = FIG_SIZE

# ----------------------------
# 1. Load Data
# ----------------------------
data_path = DEFAULT_FILE
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Data file not found at {data_path}. Place your Excel in 'data/' folder.")

xls = pd.ExcelFile(data_path)
print("Sheets found:", xls.sheet_names)
df = pd.read_excel(xls, sheet_name=0)
print(f"\n✅ Data loaded successfully! Shape: {df.shape}\n")

# ----------------------------
# 2. Basic Checks
# ----------------------------
print("🔹 First 5 Rows:")
print(df.head())
print("\n🔹 Data Info:")
df.info()
print("\n🔹 Summary Statistics:")
print(df.describe(include='all').T)
print("\n🔹 Missing Values:")
print(df.isnull().sum())

# ----------------------------
# 3. Clean Data
# ----------------------------
df = handle_missing_values(df)
print("\n✅ Missing values handled!\n")

# ----------------------------
# 4. Auto Column Detection
# ----------------------------
participation_col = find_column(df, ['participation', 'attended'])
preference_col = find_column(df, ['preference', 'company'])
gpa_col = find_column(df, ['gpa', 'cgpa', 'grade'])
field_col = find_column(df, ['field', 'department', 'major'])
gender_col = find_column(df, ['gender', 'sex'])

print("🔹 Auto-detected columns:")
print(f"Participation: {participation_col}")
print(f"Preference: {preference_col}")
print(f"GPA: {gpa_col}")
print(f"Field: {field_col}")
print(f"Gender: {gender_col}\n")

# ----------------------------
# 5. Summary Counts
# ----------------------------
if participation_col:
    print(df[participation_col].value_counts(dropna=False))
if preference_col:
    print("\nTop 10 Preferences:")
    print(df[preference_col].value_counts().head(10))
if field_col:
    print("\nTop 10 Fields:")
    print(df[field_col].value_counts().head(10))

# ----------------------------
# 6. Group Summaries
# ----------------------------
grp, participation_summary = None, None

if gpa_col and preference_col:
    grp = df.groupby(preference_col)[gpa_col].agg(['count', 'mean', 'median', 'std']).sort_values('count', ascending=False)
    print("\nAverage GPA by Company Preference:")
    print(grp)

if field_col and participation_col:
    participation_summary = pd.crosstab(df[field_col], df[participation_col], normalize='index')
    print("\nParticipation Rate by Field (rows sum to 1):")
    print(participation_summary)

# ----------------------------
# 7. Visualizations
# ----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Histograms
num_cols = df.select_dtypes(include=[np.number]).columns
for c in num_cols:
    plt.figure()
    sns.histplot(df[c], kde=True)
    plt.title(f"Histogram - {c}")
    save_plot(plt, OUTPUT_DIR, f"hist_{c}.png")
    plt.show()

# Barplot - Preferences
if preference_col:
    plt.figure()
    sns.countplot(y=df[preference_col], order=df[preference_col].value_counts().index[:15])
    plt.title("Top Company Preferences")
    save_plot(plt, OUTPUT_DIR, "bar_preference.png")
    plt.show()

# Boxplot - GPA by Preference
if gpa_col and preference_col and df[preference_col].nunique() <= 15:
    plt.figure()
    sns.boxplot(x=preference_col, y=gpa_col, data=df)
    plt.xticks(rotation=45)
    plt.title("GPA by Company Preference")
    save_plot(plt, OUTPUT_DIR, "box_gpa_preference.png")
    plt.show()

# Correlation Heatmap
if len(num_cols) > 1:
    plt.figure()
    sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Matrix")
    save_plot(plt, OUTPUT_DIR, "corr_matrix.png")
    plt.show()

# ----------------------------
# 8. Statistical Tests
# ----------------------------
# ANOVA
if gpa_col and preference_col:
    groups = [pd.to_numeric(g[gpa_col], errors='coerce').dropna() for _, g in df.groupby(preference_col)]
    groups = [g for g in groups if len(g) >= 3]
    if len(groups) >= 2:
        f_stat, p_val = stats.f_oneway(*groups)
        print(f"\n📈 ANOVA Test: GPA by Preference → F={f_stat:.4f}, p={p_val:.4g}")
    else:
        print("\n⚠️ Not enough valid groups for ANOVA.")

# Chi-square
if participation_col and preference_col:
    ct = pd.crosstab(df[participation_col], df[preference_col])
    chi2, p, dof, ex = stats.chi2_contingency(ct)
    print(f"\n📊 Chi-square Test: Participation vs Preference → chi2={chi2:.4f}, p={p:.4g}, dof={dof}")

# ----------------------------
# 9. Save Outputs
# ----------------------------
df.to_csv(os.path.join(OUTPUT_DIR, "cleaned_data.csv"), index=False)

summary_path = os.path.join(OUTPUT_DIR, "group_summaries.xlsx")
with pd.ExcelWriter(summary_path, engine="openpyxl") as writer:
    sheet_written = False
    if grp is not None:
        grp.to_excel(writer, sheet_name="GPA_by_Preference")
        sheet_written = True
    if participation_summary is not None:
        participation_summary.to_excel(writer, sheet_name="Participation_by_Field")
        sheet_written = True
    if not sheet_written:
        pd.DataFrame({"Note": ["No summaries available"]}).to_excel(writer, sheet_name="Summary_Info")

print("✅ EDA completed successfully. Outputs saved in 'outputs/' folder.")