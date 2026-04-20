import pandas as pd

df = pd.read_csv("bq-results-20260419-043458-1776573372834.csv", parse_dates=["session_date"])
print(f"Raw data: {df.shape[0]:,} rows, {df.shape[1]} cols")

# ── Step 1: Inspect missing values ─────────────────────────────────────────
# Đầu tiên mình kiểm tra xem mỗi cột có bao nhiêu giá trị bị thiếu (NaN)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_report = pd.DataFrame({
    "missing_count": missing,
    "missing_percent": missing_pct
})

# Chỉ in ra những cột thực sự có dữ liệu bị thiếu thôi
missing_report = missing_report[missing_report["missing_count"] > 0]

if missing_report.empty:
    print("Không có cột nào bị missing. Dữ liệu sạch ở bước này!")
else:
    print("Các cột bị missing:")
    print(missing_report)


# ── Step 2: Remove duplicates ───────────────────────────────────────────────
# Mỗi session phải có visit_id duy nhất, nên mình kiểm tra xem có bị trùng không
before = len(df)
df = df.drop_duplicates(subset=["visit_id"])
after = len(df)

print(f"\nStep 2 - Remove duplicates:")
print(f"  Trước: {before:,} dòng")
print(f"  Sau:   {after:,} dòng")
print(f"  Đã xóa: {before - after:,} dòng trùng")


# ── Step 3: Handle outliers ─────────────────────────────────────────────────
# Kiểm tra các giá trị bất thường ở pageviews và transaction_revenue
print("\nStep 3 - Outlier check:")
print(f"  pageviews = 0: {(df['pageviews'] == 0).sum():,} dòng")
print(f"  pageviews > 200: {(df['pageviews'] > 200).sum():,} dòng (có thể là bot)")
print(f"  transaction_revenue < 0: {(df['transaction_revenue'] < 0).sum():,} dòng")
print(f"\n  Thống kê pageviews:\n{df['pageviews'].describe().round(2)}")

# Xóa những session có pageviews = 0 vì không có ý nghĩa phân tích
before = len(df)
df = df[df["pageviews"] > 0]
print(f"\n  Đã xóa {before - len(df):,} dòng có pageviews = 0")

# Xóa những session nghi là bot (pageviews > 200)
before = len(df)
df = df[df["pageviews"] <= 200]
print(f"  Đã xóa {before - len(df):,} dòng có pageviews > 200 (bot/spam)")


# ── Step 4: Validate is_converted consistency ───────────────────────────────
# is_converted phải nhất quán với transactions:
#   - is_converted = 1 thì transactions phải > 0
#   - is_converted = 0 thì transactions phải = 0
print("\nStep 4 - Validate is_converted:")

case1 = df[(df["is_converted"] == 1) & (df["transactions"] == 0)]
case2 = df[(df["is_converted"] == 0) & (df["transactions"] > 0)]

print(f"  is_converted=1 nhưng transactions=0: {len(case1):,} dòng")
print(f"  is_converted=0 nhưng transactions>0: {len(case2):,} dòng")

# Sửa lại is_converted dựa trên transactions cho chắc
df["is_converted"] = (df["transactions"] > 0).astype(int)
print("  Đã đồng bộ lại is_converted theo transactions.")


# ── Step 5: Export cleaned data ─────────────────────────────────────────────
# Lưu ra file mới để eda_plots.py dùng, không ghi đè file gốc
output_file = "web_sessions_cleaned.csv"
df.to_csv(output_file, index=False)

print(f"\nStep 5 - Export:")
print(f"  Đã lưu file sạch: {output_file}")
print(f"  Tổng dòng sau khi clean: {len(df):,}")
