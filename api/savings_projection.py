import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

days = np.arange(1, 31)

status_quo_monthly_bill = 175.00
circuit_saver_monthly_bill = 135.00

status_quo_daily = status_quo_monthly_bill / 30
circuit_saver_daily = circuit_saver_monthly_bill / 30

status_quo_cumulative = days * status_quo_daily
circuit_saver_cumulative = days * circuit_saver_daily
monthly_savings = status_quo_monthly_bill - circuit_saver_monthly_bill
savings_pct = (monthly_savings / status_quo_monthly_bill) * 100

plt.figure(figsize=(11, 6))
plt.plot(
    days,
    status_quo_cumulative,
    label="Status Quo (No Savings)",
    color="#9CA3AF",
    linewidth=3,
    linestyle="--"
)
plt.plot(
    days,
    circuit_saver_cumulative,
    label="CircuitSaver User",
    color="#16A34A",
    linewidth=4
)

plt.fill_between(
    days,
    circuit_saver_cumulative,
    status_quo_cumulative,
    color="#86EFAC",
    alpha=0.35,
    label=f"Monthly Savings: ${monthly_savings:.0f}"
)

plt.scatter([30], [status_quo_cumulative[-1]], color="#6B7280", s=80)
plt.scatter([30], [circuit_saver_cumulative[-1]], color="#15803D", s=80)

plt.annotate(
    f"${status_quo_monthly_bill:.0f}",
    (30, status_quo_cumulative[-1]),
    textcoords="offset points",
    xytext=(8, 6),
    fontsize=12,
    fontweight="bold",
    color="#4B5563"
)

plt.annotate(
    f"${circuit_saver_monthly_bill:.0f}",
    (30, circuit_saver_cumulative[-1]),
    textcoords="offset points",
    xytext=(8, -18),
    fontsize=12,
    fontweight="bold",
    color="#166534"
)

plt.text(
    17,
    (status_quo_cumulative[16] + circuit_saver_cumulative[16]) / 2,
    f"CircuitSaver saves about ${monthly_savings:.0f}/month\n({savings_pct:.1f}% lower bill)",
    fontsize=12,
    fontweight="bold",
    color="#14532D",
    ha="center",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#86EFAC", alpha=0.95)
)

plt.title("Projected Monthly Electricity Cost: Status Quo vs CircuitSaver")
plt.xlabel("Day of Month")
plt.ylabel("Cumulative Electricity Cost (USD)")
plt.xlim(1, 30)
plt.ylim(0, max(status_quo_cumulative) * 1.1)
plt.grid(True, alpha=0.25)
plt.legend(frameon=True)
plt.tight_layout()
plt.savefig("circuitsaver_monthly_cost_comparison.png", dpi=220)
plt.close()

print(f"Status quo monthly bill: ${status_quo_monthly_bill:.2f}")
print(f"CircuitSaver monthly bill: ${circuit_saver_monthly_bill:.2f}")
print(f"Monthly savings: ${monthly_savings:.2f}")
print(f"Percent savings: {savings_pct:.2f}%")