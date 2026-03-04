import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Default file name
DEFAULT_FILE = os.path.join(DATA_DIR, "Data Analysis.xlsx")

# Plot settings
FIG_SIZE = (10, 6)
STYLE = "whitegrid"