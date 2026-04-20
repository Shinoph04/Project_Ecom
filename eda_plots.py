import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("web_sessions_cleaned.csv", parse_dates=["session_date"])

def save_fig(fig, filename):
    fig.tight_layout()
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {filename}")

# ── Page 1: Traffic & Acquisition ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Page 1 — Traffic & Acquisition", fontsize=14, fontweight="bold")

# 1a. Sessions over time
ax = axes[0, 0]
sessions_by_date = df.groupby("session_date").size()
ax.plot(sessions_by_date.index, sessions_by_date.values, color="#4e79a7", linewidth=1.5)
ax.set_title("Sessions Over Time")
ax.set_ylabel("Sessions")
ax.tick_params(axis="x", rotation=30)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 1b. Top 10 traffic sources
ax = axes[0, 1]
top_sources = df["traffic_source"].value_counts().head(10)
ax.barh(top_sources.index[::-1], top_sources.values[::-1], color="#4e79a7")
ax.set_title("Top 10 Traffic Sources")
ax.set_xlabel("Sessions")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 1c. Traffic medium breakdown
ax = axes[1, 0]
medium_counts = df["traffic_medium"].value_counts().head(8)
ax.bar(medium_counts.index, medium_counts.values, color="#76b7b2")
ax.set_title("Sessions by Traffic Medium")
ax.set_ylabel("Sessions")
ax.tick_params(axis="x", rotation=30)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 1d. Top 10 countries
ax = axes[1, 1]
top_countries = df["country"].value_counts().head(10)
ax.barh(top_countries.index[::-1], top_countries.values[::-1], color="#f28e2b")
ax.set_title("Top 10 Countries by Sessions")
ax.set_xlabel("Sessions")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

save_fig(fig, "page1_traffic_acquisition.png")

# ── Page 2: Conversion Analysis ────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Page 2 — Conversion Analysis", fontsize=14, fontweight="bold")

# 2a. Overall conversion rate
ax = axes[0, 0]
sizes = df["is_converted"].value_counts().sort_index().values
ax.pie(sizes, labels=["Not Converted", "Converted"], colors=["#d9534f", "#5cb85c"],
       autopct="%1.1f%%", startangle=90)
ax.set_title("Overall Conversion Rate")

# 2b. Conversion rate by device
ax = axes[0, 1]
conv_device = df.groupby("device_category")["is_converted"].mean() * 100
bars = ax.bar(conv_device.index, conv_device.values, color=["#4e79a7", "#f28e2b", "#76b7b2"])
ax.set_title("Conversion Rate by Device")
ax.set_ylabel("Conversion Rate (%)")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"{bar.get_height():.2f}%", ha="center", fontsize=10)

# 2c. Conversion rate by top 8 traffic sources
ax = axes[1, 0]
top8_sources = df["traffic_source"].value_counts().head(8).index
conv_source = (df[df["traffic_source"].isin(top8_sources)]
               .groupby("traffic_source")["is_converted"].mean()
               .mul(100)
               .sort_values(ascending=True))
ax.barh(conv_source.index, conv_source.values, color="#59a14f")
ax.set_title("Conversion Rate by Traffic Source (Top 8)")
ax.set_xlabel("Conversion Rate (%)")

# 2d. Conversion rate over time
ax = axes[1, 1]
conv_by_date = df.groupby("session_date")["is_converted"].mean() * 100
ax.plot(conv_by_date.index, conv_by_date.values, color="#5cb85c", linewidth=1.5)
ax.set_title("Conversion Rate Over Time")
ax.set_ylabel("Conversion Rate (%)")
ax.tick_params(axis="x", rotation=30)

save_fig(fig, "page2_conversion.png")

# ── Page 3: Device & User Behavior ─────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Page 3 — Device & User Behavior", fontsize=14, fontweight="bold")

# 3a. Sessions by device
ax = axes[0, 0]
device_counts = df["device_category"].value_counts()
ax.pie(device_counts.values, labels=device_counts.index,
       colors=["#4e79a7", "#f28e2b", "#76b7b2"], autopct="%1.1f%%", startangle=90)
ax.set_title("Sessions by Device Category")

# 3b. Avg pageviews by device
ax = axes[0, 1]
avg_pv = df.groupby("device_category")["pageviews"].mean().sort_values(ascending=False)
bars = ax.bar(avg_pv.index, avg_pv.values, color=["#4e79a7", "#f28e2b", "#76b7b2"])
ax.set_title("Avg Pageviews per Session by Device")
ax.set_ylabel("Avg Pageviews")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            f"{bar.get_height():.2f}", ha="center", fontsize=10)

# 3c. Pageviews distribution (capped at 20)
ax = axes[1, 0]
pv_capped = df["pageviews"].clip(upper=20)
ax.hist(pv_capped, bins=20, color="#4e79a7", edgecolor="white")
ax.set_title("Pageviews Distribution (capped at 20)")
ax.set_xlabel("Pageviews")
ax.set_ylabel("Sessions")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 3d. Device mix over time (area chart)
ax = axes[1, 1]
device_time = (df.groupby(["session_date", "device_category"])
               .size().unstack(fill_value=0))
device_time_pct = device_time.div(device_time.sum(axis=1), axis=0) * 100
device_time_pct.plot.area(ax=ax, color=["#4e79a7", "#f28e2b", "#76b7b2"], alpha=0.8, legend=True)
ax.set_title("Device Mix Over Time (%)")
ax.set_ylabel("%")
ax.tick_params(axis="x", rotation=30)
ax.legend(loc="upper right", fontsize=8)

save_fig(fig, "page3_device_behavior.png")
