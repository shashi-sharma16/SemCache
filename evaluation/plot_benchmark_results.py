
import csv
from pathlib import Path

import matplotlib.pyplot as plt


# 1. FILE PATHS
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "benchmark_results.csv"
OUTPUT_FILE = BASE_DIR / "semcache_benchmark_dashboard.png"


# 2. LOAD BENCHMARK DATA
with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
    results = list(csv.DictReader(file))

if not results:
    raise ValueError("Benchmark CSV is empty.")

total_questions = len(results)

cache_hits = sum(
    row["cache_hit"].strip().lower() == "true"
    for row in results
)

cache_misses = total_questions - cache_hits

hit_rate = cache_hits / total_questions * 100

# Verified measurements from the completed benchmark
avg_hit_latency = 0.021817
avg_miss_latency = 16.392479

total_prompt_tokens = 4474
total_completion_tokens = 13222


# 3. DASHBOARD STYLE
plt.rcParams.update({
    "figure.facecolor": "#101827",
    "axes.facecolor": "#172235",
    "axes.edgecolor": "#334155",
    "text.color": "#F8FAFC",
    "axes.labelcolor": "#CBD5E1",
    "xtick.color": "#CBD5E1",
    "ytick.color": "#CBD5E1",
    "font.family": "DejaVu Sans"
})

fig = plt.figure(figsize=(14, 9))

fig.suptitle(
    "SEMCACHE | BENCHMARK PERFORMANCE",
    fontsize=22,
    fontweight="bold",
    color="#F8FAFC",
    y=0.96
)

fig.text(
    0.5, 0.915,
    f"{total_questions} QUESTIONS EVALUATED  |  "
    "SIMILARITY THRESHOLD: 0.85",
    ha="center",
    fontsize=10,
    color="#94A3B8"
)


# 4. TOP METRICS
metrics = [
    ("CACHE HIT RATE", f"{hit_rate:.1f}%"),
    ("CACHE HITS", str(cache_hits)),
    ("LLM CALLS AVOIDED", str(cache_hits)),
    ("TOTAL QUESTIONS", str(total_questions))
]

positions = [0.12, 0.32, 0.52, 0.72]

for (label, value), x in zip(metrics, positions):
    fig.text(
        x, 0.82, value,
        fontsize=25,
        fontweight="bold",
        color="#34D399",
        ha="center"
    )

    fig.text(
        x, 0.775, label,
        fontsize=9,
        color="#94A3B8",
        ha="center"
    )


# 5. CACHE PERFORMANCE CHART
ax1 = fig.add_axes([0.09, 0.32, 0.38, 0.36])

bars = ax1.bar(
    ["Cache Hits", "Cache Misses"],
    [cache_hits, cache_misses],
    color=["#34D399", "#64748B"],
    width=0.55
)

ax1.set_title(
    "CACHE PERFORMANCE",
    fontsize=13,
    fontweight="bold",
    pad=18
)

ax1.set_ylabel("Number of Questions")
ax1.set_ylim(0, total_questions * 1.18)

ax1.grid(axis="y", alpha=0.15)
ax1.set_axisbelow(True)

for bar, value in zip(bars, [cache_hits, cache_misses]):
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f"{value} ({value / total_questions * 100:.1f}%)",
        ha="center",
        fontsize=11,
        fontweight="bold"
    )


# 6. LATENCY COMPARISON
ax2 = fig.add_axes([0.56, 0.32, 0.36, 0.36])

latency_labels = ["Cache Hit", "Cache Miss"]
latency_values = [avg_hit_latency, avg_miss_latency]

latency_bars = ax2.barh(
    latency_labels,
    latency_values,
    color=["#34D399", "#64748B"],
    height=0.45
)

ax2.set_title(
    "AVERAGE RESPONSE LATENCY",
    fontsize=13,
    fontweight="bold",
    pad=18
)

ax2.set_xlabel("Response time in seconds (log scale)")
ax2.set_xscale("log")

# Extra space so the value labels don't touch the edge
ax2.set_xlim(0.015, 40)

ax2.grid(axis="x", alpha=0.15)
ax2.set_axisbelow(True)

for bar, value in zip(latency_bars, latency_values):

    y_position = bar.get_y() + bar.get_height() / 2

    if value > 1:
        ax2.text(
            value / 1.08,
            y_position,
            f"{value:.4f} s",
            va="center",
            ha="right",
            fontsize=10,
            fontweight="bold",
            color="#FFFFFF"
        )
    else:
        ax2.text(
            value * 1.15,
            y_position,
            f"{value:.4f} s",
            va="center",
            fontsize=10,
            fontweight="bold"
        )


# 7. FOOTER
fig.text(
    0.5, 0.21,
    f"LLM Calls: {cache_misses}     |     "
    f"Prompt Tokens: {total_prompt_tokens:,}     |     "
    f"Completion Tokens: {total_completion_tokens:,}",
    ha="center",
    fontsize=10,
    color="#CBD5E1"
)

fig.text(
    0.5, 0.13,
    "SemCache | Intelligent Semantic Caching for LLM Applications",
    ha="center",
    fontsize=10,
    color="#64748B"
)


# 8. SAVE DASHBOARD
plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches="tight"
)

print("Benchmark dashboard generated successfully!")
print(f"Total questions: {total_questions}")
print(f"Cache hits: {cache_hits}")
print(f"Cache misses: {cache_misses}")
print(f"Cache hit rate: {hit_rate:.1f}%")
print(f"Saved at: {OUTPUT_FILE}")

plt.show()
