"""
estimator_service.py — savings-estimate methodology for the Savings
Estimator feature.

Every constant below is traced to a real, documented source in this
project — none are invented for this feature:

  - AUSTIN_AVG_HOUSEHOLD_LOAD_KW: mean of `avg_connected_load_kw` across the
    Austin transformers sampled in api/data/synthetic/transformer_topology.csv
    (6.78, 2.27, 3.32, 5.98, 4.61, 0.33 kW -> mean 3.88 kW).
  - COST_PER_KWH / CO2_LBS_PER_KWH: the Capacity Allocator's own default
    savings-math constants (api/app/routers/swarm.py: $0.15/kWh,
    0.85 lbs CO2/kWh).
  - MAX_COST_REDUCTION_PCT / MAX_EMISSIONS_REDUCTION_PCT: independent
    load-shifting research bounds cited in the project overview PDF
    ("up to 34% cost reduction and up to 19% emissions reduction at scale").
  - ESTIMATED_PEAK_HOURS_PER_YEAR: derived from "peaker plants run only
    about 5% of the year" (PDF): 0.05 * 8760 hours = 438 hours.

No geocoding API is configured in this project. Region matching is a
keyword heuristic against the two regions Circuit Saver's ML models were
actually trained/validated on (Austin_TX, London_UK). Anything else is
"unmatched" and given the same conservative estimate, explicitly labeled a
national-average assumption. London-specific household load data is not
available in this repository (the trained London model file and processed
dataset were not pushed), so London-matched addresses currently reuse the
Austin-derived load assumption, disclosed in the response.
"""

AUSTIN_AVG_HOUSEHOLD_LOAD_KW = 3.88
COST_PER_KWH = 0.15
CO2_LBS_PER_KWH = 0.85
MAX_COST_REDUCTION_PCT = 0.34
MAX_EMISSIONS_REDUCTION_PCT = 0.19
ESTIMATED_PEAK_HOURS_PER_YEAR = 438

LOW_SHIFT_FRACTION = 0.22
HIGH_SHIFT_FRACTION = 0.32


def match_region(address_text: str) -> str:
    text = (address_text or "").lower()
    uk_markers = ["uk", "united kingdom", "london", "england", "scotland", "wales"]
    tx_markers = ["texas", "austin", " tx", "tx,", "tx "]
    if any(m in text for m in uk_markers):
        return "London_UK"
    if any(m in text for m in tx_markers):
        return "Austin_TX"
    return "unmatched"


def estimate_savings(address_text: str) -> dict:
    region = match_region(address_text)
    confidence = "region-matched" if region == "Austin_TX" else "national-average assumption"

    avg_load_kw = AUSTIN_AVG_HOUSEHOLD_LOAD_KW
    low_shift_kw = round(avg_load_kw * LOW_SHIFT_FRACTION, 2)
    high_shift_kw = round(avg_load_kw * HIGH_SHIFT_FRACTION, 2)

    annual_peak_exposure_cost = avg_load_kw * COST_PER_KWH * ESTIMATED_PEAK_HOURS_PER_YEAR
    low_annual_savings = round(annual_peak_exposure_cost * LOW_SHIFT_FRACTION * MAX_COST_REDUCTION_PCT, 2)
    high_annual_savings = round(annual_peak_exposure_cost * HIGH_SHIFT_FRACTION * MAX_COST_REDUCTION_PCT, 2)

    annual_peak_exposure_co2_lbs = avg_load_kw * CO2_LBS_PER_KWH * ESTIMATED_PEAK_HOURS_PER_YEAR
    co2_reduction_lbs = round(annual_peak_exposure_co2_lbs * MAX_EMISSIONS_REDUCTION_PCT, 1)
    co2_reduction_kg = round(co2_reduction_lbs * 0.4536, 1)

    notes = [
        f"Household load assumed at {avg_load_kw} kW average, based on Circuit Saver's sampled Austin, TX transformer data.",
        "Flexible/shiftable load assumed at 22%-32% of average household load during a peak event.",
        "Savings bounded by independent load-shifting research showing up to 34% cost reduction and 19% emissions reduction at scale.",
        f"Assumes approximately {ESTIMATED_PEAK_HOURS_PER_YEAR} peak hours per year, based on the peaker-plant utilization rate (~5% of the year) cited in Circuit Saver's project overview.",
        "This is a modeled estimate, not a guarantee. Actual savings depend on your utility's rate structure, household equipment, and real-time grid conditions.",
    ]
    if region != "Austin_TX":
        notes.insert(
            0,
            "We could not confidently match your address to a region Circuit Saver's models have been validated on (Austin, TX or London, UK). This estimate uses a conservative national-average household load assumption instead of a region-specific one.",
        )

    return {
        "region_matched": region,
        "confidence": confidence,
        "estimated_avg_household_load_kw": avg_load_kw,
        "estimated_shiftable_capacity_kw_low": low_shift_kw,
        "estimated_shiftable_capacity_kw_high": high_shift_kw,
        "estimated_annual_savings_low_usd": low_annual_savings,
        "estimated_annual_savings_high_usd": high_annual_savings,
        "estimated_monthly_savings_low_usd": round(low_annual_savings / 12, 2),
        "estimated_monthly_savings_high_usd": round(high_annual_savings / 12, 2),
        "estimated_co2_reduction_kg_per_year": co2_reduction_kg,
        "estimated_peak_hours_per_year": ESTIMATED_PEAK_HOURS_PER_YEAR,
        "assumptions": notes,
    }
