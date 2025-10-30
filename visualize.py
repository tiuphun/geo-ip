import matplotlib.pyplot as plt
import numpy as np

# Use a clean, professional font and style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'axes.edgecolor': 'black',
    'axes.linewidth': 0.8,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9
})

# Data
cities = [
    "Unknown", "Taipei", "Taichung", "New Taipei City", "Chiayi County",
    "Taoyuan District", "Kaohsiung", "Tainan City", "Zhongli District",
    "Songshan", "East District", "Yuanlin", "Xitun", "Hsinchu", "Taoyuan",
    "Zhubei", "Hsinchu County", "Anping District", "Neihu District", "Yilan",
    "Keelung", "Chang-hua", "Pingzhen", "Xinzhuang District"
]
counts = [
    324, 67, 49, 26, 20, 15, 13, 10, 5, 4, 4, 4, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1
]

# Sort by count descending
sorted_indices = np.argsort(counts)[::-1]
cities_sorted = [cities[i] for i in sorted_indices]
counts_sorted = [counts[i] for i in sorted_indices]

# Calculate percentages
total = sum(counts_sorted)
percentages = [c / total * 100 for c in counts_sorted]

# Plot
fig, ax = plt.subplots(figsize=(9, 8))
bars = ax.barh(cities_sorted[::-1], counts_sorted[::-1], color='gray', edgecolor='black')

# Add percentage labels
for bar, pct in zip(bars, percentages[::-1]):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
            f"{pct:.1f}%", va='center', fontsize=8, color='black')

# Axis labels and title
ax.set_xlabel("Count")
ax.set_ylabel("City / District")
ax.set_title("Estimated City Distribution of IP Addresses in Taiwan\n(Based on MaxMind GeoLite2-City Database)")

# Grid and spine style
ax.grid(axis='x', linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()
