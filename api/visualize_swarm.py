"""
visualize_swarm.py
Generates presentation-ready charts from swarm_engine.py's allocation output.
Run this from the api/ directory.
"""

import os
import plotly.graph_objects as go
from app.services.optimizer.swarm_engine import allocate_capacity, load_transformers

OUTPUT_DIR = "swarm_eval_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def style_fig(fig, ytitle, xtitle, y_range=None):
    fig.update_layout(
        template="plotly_white",
        font=dict(size=16, color="#1a1a1a"),
        title_font=dict(size=20, color="#1a1a1a"),
        legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='center', x=0.5, font=dict(size=14)),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=110, b=60, l=70, r=30),
    )
    fig.update_xaxes(title_text=xtitle, title_font=dict(size=15), tickfont=dict(size=14, color="#1a1a1a"),
                      showgrid=False, linecolor="#888", linewidth=1)
    fig.update_yaxes(title_text=ytitle, title_font=dict(size=15), tickfont=dict(size=14, color="#1a1a1a"),
                      gridcolor="#e0e0e0", zeroline=False, range=y_range)
    fig.update_traces(cliponaxis=False)
    return fig

COLOR1, COLOR2, COLOR3, COLOR4 = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"

transformers = load_transformers()
transformer_id = transformers.iloc[0]["transformer_id"]
shed_target_kw = 5.0

summary, result = allocate_capacity(
    transformer_id=transformer_id,
    shed_target_kw=shed_target_kw,
)

print("=== Allocation Summary ===")
for k, v in summary.items():
    print(f"{k}: {v}")

fig1 = go.Figure()
fig1.add_bar(
    x=result["user_id"], y=result["allocated_kw"],
    text=[f"{v:.2f}" for v in result["allocated_kw"]], textposition="outside",
    marker_color=[COLOR4 if c else COLOR1 for c in result["is_capped"]],
)
fig1.update_layout(title={"text": f"Per-Household Load Shed Allocation ({transformer_id})<br><span style='font-size:14px;font-weight:normal;color:#555'>Red = capped at max shiftable capacity | Target: {shed_target_kw} kW</span>"})
style_fig(fig1, "Allocated (kW)", "Household")
fig1.write_image(f"{OUTPUT_DIR}/allocation_per_household.png", scale=2)

fig2 = go.Figure()
fig2.add_bar(name="Allocated", x=result["user_id"], y=result["allocated_kw"], marker_color=COLOR1)
fig2.add_bar(name="Remaining Capacity", x=result["user_id"],
             y=result["shiftable_capacity_kwh"] - result["allocated_kw"], marker_color="#d9d9d9")
fig2.update_layout(barmode="stack", title={"text": "Allocated vs Remaining Shiftable Capacity<br><span style='font-size:14px;font-weight:normal;color:#555'>Shows available headroom per household</span>"})
style_fig(fig2, "Energy (kWh)", "Household")
fig2.write_image(f"{OUTPUT_DIR}/allocation_vs_capacity.png", scale=2)

fig3 = go.Figure()
fig3.add_scatter(
    x=result["priority_score"], y=result["allocated_kw"], mode="markers",
    marker=dict(size=12, color=COLOR2, line=dict(width=1, color="#1a1a1a")),
    text=result["user_id"], hovertemplate="%{text}<br>Priority: %{x:.3f}<br>Allocated: %{y:.2f} kW",
)
fig3.update_layout(title={"text": "Priority Score vs Allocated Load Shed<br><span style='font-size:14px;font-weight:normal;color:#555'>Higher priority households shed more, as designed</span>"})
style_fig(fig3, "Allocated (kW)", "Priority Score")
fig3.write_image(f"{OUTPUT_DIR}/priority_vs_allocation.png", scale=2)

fig4 = go.Figure()
fig4.add_bar(name="Cost Saved ($)", x=result["user_id"], y=result["estimated_cost_saved_usd"], marker_color=COLOR3)
fig4.update_layout(title={"text": "Estimated Cost Savings per Household<br><span style='font-size:14px;font-weight:normal;color:#555'>Based on peak rate assumption in swarm_engine.py</span>"})
style_fig(fig4, "Cost Saved ($)", "Household")
fig4.write_image(f"{OUTPUT_DIR}/cost_saved_per_household.png", scale=2)

fig5 = go.Figure()
fig5.add_bar(name="Carbon Saved (lbs)", x=result["user_id"], y=result["estimated_carbon_saved_lbs"], marker_color=COLOR4)
fig5.update_layout(title={"text": "Estimated Carbon Savings per Household<br><span style='font-size:14px;font-weight:normal;color:#555'>Based on CO2 intensity assumption in swarm_engine.py</span>"})
style_fig(fig5, "Carbon Saved (lbs)", "Household")
fig5.write_image(f"{OUTPUT_DIR}/carbon_saved_per_household.png", scale=2)

by_type = result.groupby("household_type")["allocated_kw"].sum().reset_index().sort_values("allocated_kw", ascending=False)
fig6 = go.Figure()
fig6.add_bar(x=by_type["household_type"], y=by_type["allocated_kw"],
             text=[f"{v:.2f}" for v in by_type["allocated_kw"]], textposition="outside", marker_color=COLOR1)
fig6.update_layout(title={"text": "Total Load Shed by Household Type<br><span style='font-size:14px;font-weight:normal;color:#555'>Aggregated across all households on transformer</span>"})
style_fig(fig6, "Total Allocated (kW)", "Household Type")
fig6.write_image(f"{OUTPUT_DIR}/allocation_by_household_type.png", scale=2)

fig7 = go.Figure()
fig7.add_bar(
    x=["Shed Target", "Total Allocated", "Shortfall"],
    y=[summary["shed_target_kw"], summary["total_allocated_kw"], summary["shortfall_kw"]],
    text=[f"{v:.2f}" for v in [summary["shed_target_kw"], summary["total_allocated_kw"], summary["shortfall_kw"]]],
    textposition="outside", marker_color=[COLOR1, COLOR3, COLOR4], width=0.5,
)
fig7.update_layout(title={"text": f"Load Shed Target vs Achieved ({transformer_id})<br><span style='font-size:14px;font-weight:normal;color:#555'>{summary['households_involved']} households involved</span>"})
style_fig(fig7, "Power (kW)", "Metric")
fig7.write_image(f"{OUTPUT_DIR}/target_vs_achieved.png", scale=2)

print(f"\nCharts saved to: {OUTPUT_DIR}/")