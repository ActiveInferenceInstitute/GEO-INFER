# Basic Example: Temperature Anomaly Detection

This example walks through loading synthetic climate data, computing a 30-year climatology baseline, detecting temperature anomalies, and assessing their statistical significance.

## Problem Setup

We have 50 years (1970-2019) of monthly mean temperature data for a single station. The goal is to identify months where temperatures deviate significantly from the 1971-2000 climatological normal.

```python
import numpy as np
from geo_infer_climate.core.temperature_trends import TemperatureTrendAnalyzer

np.random.seed(42)

# Generate 50 years of monthly temperature data
years = np.arange(1970, 2020)
months = np.arange(1, 13)
n_years = len(years)

# Monthly climatological means (deg C) for a temperate location
monthly_means = np.array([2.1, 3.5, 7.2, 11.8, 16.4, 20.1, 22.3, 21.5, 17.8, 12.4, 7.1, 3.2])

# Monthly standard deviations
monthly_stds = np.array([2.5, 2.8, 2.3, 1.9, 1.7, 1.5, 1.3, 1.4, 1.6, 1.8, 2.2, 2.6])

# Build the time series with warming trend and natural variability
warming_rate = 0.018  # deg C per year

temperatures = np.zeros(n_years * 12)
year_labels = np.zeros(n_years * 12, dtype=int)
month_labels = np.zeros(n_years * 12, dtype=int)

for y_idx, year in enumerate(years):
    for m_idx in range(12):
        idx = y_idx * 12 + m_idx
        warming = warming_rate * (year - 1970)
        noise = np.random.normal(0, monthly_stds[m_idx])
        temperatures[idx] = monthly_means[m_idx] + warming + noise
        year_labels[idx] = year
        month_labels[idx] = m_idx + 1

print(f"Total months: {len(temperatures)}")
print(f"Period: {years[0]} to {years[-1]}")
print(f"Temperature range: {temperatures.min():.1f} to {temperatures.max():.1f} deg C")
```

## Step 1: Compute the Climatological Baseline

Define the 1971-2000 reference period and compute monthly normals.

```python
# Extract reference period (1971-2000)
ref_mask = (year_labels >= 1971) & (year_labels <= 2000)
ref_temps = temperatures[ref_mask]
ref_months = month_labels[ref_mask]

# Compute monthly climatological normals
climatology = {}
for m in range(1, 13):
    month_data = ref_temps[ref_months == m]
    climatology[m] = {
        'mean': np.mean(month_data),
        'std': np.std(month_data),
        'p10': np.percentile(month_data, 10),
        'p90': np.percentile(month_data, 90),
    }

print("\n--- 1971-2000 Climatological Normals ---")
month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
print(f"{'Month':<6} {'Mean':>7} {'Std':>7} {'P10':>7} {'P90':>7}")
for m in range(1, 13):
    c = climatology[m]
    print(f"{month_names[m-1]:<6} {c['mean']:>7.2f} {c['std']:>7.2f} "
          f"{c['p10']:>7.2f} {c['p90']:>7.2f}")
```

## Step 2: Compute Anomalies

Calculate the departure of each month from its climatological normal.

```python
# Compute anomalies
anomalies = np.zeros_like(temperatures)
standardized_anomalies = np.zeros_like(temperatures)

for i in range(len(temperatures)):
    m = month_labels[i]
    c = climatology[m]
    anomalies[i] = temperatures[i] - c['mean']
    standardized_anomalies[i] = anomalies[i] / c['std'] if c['std'] > 0 else 0.0

print(f"\n--- Anomaly Statistics ---")
print(f"Mean anomaly: {np.mean(anomalies):+.3f} deg C")
print(f"Anomaly range: {anomalies.min():+.2f} to {anomalies.max():+.2f} deg C")
print(f"Std of anomalies: {np.std(anomalies):.3f} deg C")
```

## Step 3: Flag Significant Anomalies

Flag months where standardized anomalies exceed +/- 2 standard deviations.

```python
# Detect warm and cold anomalies
warm_threshold = 2.0   # standard deviations above normal
cold_threshold = -2.0  # standard deviations below normal

warm_anomalies = []
cold_anomalies = []

for i in range(len(temperatures)):
    if standardized_anomalies[i] >= warm_threshold:
        warm_anomalies.append({
            'year': int(year_labels[i]),
            'month': int(month_labels[i]),
            'temperature': float(temperatures[i]),
            'anomaly': float(anomalies[i]),
            'z_score': float(standardized_anomalies[i]),
        })
    elif standardized_anomalies[i] <= cold_threshold:
        cold_anomalies.append({
            'year': int(year_labels[i]),
            'month': int(month_labels[i]),
            'temperature': float(temperatures[i]),
            'anomaly': float(anomalies[i]),
            'z_score': float(standardized_anomalies[i]),
        })

print(f"\n--- Significant Warm Anomalies (z >= {warm_threshold}) ---")
print(f"Count: {len(warm_anomalies)} months out of {len(temperatures)} ({len(warm_anomalies)/len(temperatures)*100:.1f}%)")
for event in warm_anomalies[:10]:
    mname = month_names[event['month'] - 1]
    print(f"  {event['year']} {mname}: {event['temperature']:.1f} deg C "
          f"(anomaly={event['anomaly']:+.2f}, z={event['z_score']:.2f})")

if len(warm_anomalies) > 10:
    print(f"  ... and {len(warm_anomalies) - 10} more")

print(f"\n--- Significant Cold Anomalies (z <= {cold_threshold}) ---")
print(f"Count: {len(cold_anomalies)} months out of {len(temperatures)} ({len(cold_anomalies)/len(temperatures)*100:.1f}%)")
for event in cold_anomalies[:10]:
    mname = month_names[event['month'] - 1]
    print(f"  {event['year']} {mname}: {event['temperature']:.1f} deg C "
          f"(anomaly={event['anomaly']:+.2f}, z={event['z_score']:.2f})")
```

## Step 4: Trend Analysis on Anomalies

Apply both parametric and non-parametric trend tests to the annual mean anomaly time series.

```python
analyzer = TemperatureTrendAnalyzer()

# Compute annual mean temperatures
annual_means = []
for year in years:
    mask = year_labels == year
    annual_means.append(np.mean(temperatures[mask]))
annual_means = np.array(annual_means)

# Compute annual mean anomalies (relative to baseline mean)
baseline_mean = np.mean([climatology[m]['mean'] for m in range(1, 13)])
annual_anomalies = annual_means - baseline_mean

# Linear regression on annual means
trend = analyzer.linear_trend(annual_means, years.astype(float))

print("\n--- Annual Temperature Trend (Linear Regression) ---")
print(f"Slope: {trend['slope']:.5f} deg C/year")
print(f"Per decade: {trend['slope_per_decade']:.3f} deg C/decade")
print(f"R-squared: {trend['r_squared']:.4f}")
print(f"P-value: {trend['p_value']:.6f}")
if trend['p_value'] < 0.05:
    print("Result: Statistically significant warming trend (p < 0.05)")
else:
    print("Result: No statistically significant trend")

# Mann-Kendall on annual means
mk = analyzer.mann_kendall_test(annual_means, alpha=0.05)

print("\n--- Annual Temperature Trend (Mann-Kendall) ---")
print(f"Trend: {mk['trend']}")
print(f"S statistic: {mk['s_statistic']:.0f}")
print(f"Z-score: {mk['z_score']:.4f}")
print(f"P-value: {mk['p_value']:.6f}")
print(f"Sen's slope: {mk['sens_slope']:.5f} deg C/year")
print(f"Sen's slope per decade: {mk['sens_slope'] * 10:.3f} deg C/decade")
```

## Step 5: Decadal Comparison

Compare anomaly frequency and magnitude across decades.

```python
print("\n--- Decadal Anomaly Summary ---")
print(f"{'Decade':<10} {'Mean Anom':>10} {'Warm Events':>12} {'Cold Events':>12} {'Mean Temp':>10}")

for decade_start in [1970, 1980, 1990, 2000, 2010]:
    decade_end = decade_start + 9
    decade_mask = (year_labels >= decade_start) & (year_labels <= decade_end)

    decade_anomalies = anomalies[decade_mask]
    decade_std_anomalies = standardized_anomalies[decade_mask]

    mean_anom = np.mean(decade_anomalies)
    n_warm = np.sum(decade_std_anomalies >= warm_threshold)
    n_cold = np.sum(decade_std_anomalies <= cold_threshold)
    mean_temp = np.mean(temperatures[decade_mask])

    print(f"{decade_start}s    {mean_anom:>+10.3f} {n_warm:>12d} {n_cold:>12d} {mean_temp:>10.2f}")
```

## Expected Output

```
--- 1971-2000 Climatological Normals ---
Month    Mean     Std     P10     P90
Jan      2.33    2.54   -0.84    5.67
Feb      3.78    2.82    0.43    7.35
...

--- Significant Warm Anomalies (z >= 2.0) ---
Count: 14 months out of 600 (2.3%)
  2015 Jul: 25.1 deg C (anomaly=+2.87, z=2.21)
  2018 Aug: 24.9 deg C (anomaly=+3.12, z=2.23)
  ...

--- Annual Temperature Trend (Linear Regression) ---
Slope: 0.01842 deg C/year
Per decade: 0.184 deg C/decade
R-squared: 0.4231
P-value: 0.000002
Result: Statistically significant warming trend (p < 0.05)

--- Annual Temperature Trend (Mann-Kendall) ---
Trend: increasing
Sen's slope: 0.01798 deg C/year
```

The analysis confirms a statistically significant warming trend of approximately 0.18 deg C per decade, with increasing warm anomaly frequency in recent decades.
