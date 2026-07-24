const TOTAL_HOMES_WORLD = 2_100_000_000;
const ENERGY_PER_HOME_MWH = 10.5;
const COST_PER_MWH = 148;
const EMISSIONS_PER_MWH_KG = 386;

function calcMetrics(pct) {
  const homes = Math.round((pct / 100) * TOTAL_HOMES_WORLD);
  const energyMWh = Math.round(homes * ENERGY_PER_HOME_MWH);
  const moneySaved = Math.round(energyMWh * COST_PER_MWH);
  const emissionsKg = Math.round(energyMWh * EMISSIONS_PER_MWH_KG);
  return { homes, energyMWh, moneySaved, emissionsKg };
}

function formatLarge(n) {
  if (n >= 1e9) return { value: (n / 1e9).toFixed(2), unit: "B" };
  if (n >= 1e6) return { value: (n / 1e6).toFixed(1), unit: "M" };
  if (n >= 1e3) return { value: (n / 1e3).toFixed(1), unit: "K" };
  return { value: String(n), unit: "" };
}

function initImpactSlider() {
  const slider = document.getElementById("impact-slider");
  if (!slider) return;
  const heading = document.getElementById("impact-pct-heading");

  function render(pct) {
    const m = calcMetrics(pct);
    const homeFmt = formatLarge(m.homes);
    const moneyFmt = formatLarge(m.moneySaved);
    const energyFmt = formatLarge(m.energyMWh);
    const emissionsFmt = formatLarge(m.emissionsKg / 1000);

    heading.textContent = pct;
    slider.style.background = `linear-gradient(to right, #56d16d ${pct}%, #e5e7eb ${pct}%)`;

    document.getElementById("card-homes-value").textContent = homeFmt.value;
    document.getElementById("card-homes-unit").textContent = homeFmt.unit;
    document.getElementById("card-energy-value").textContent = energyFmt.value;
    document.getElementById("card-energy-unit").textContent = `${energyFmt.unit} MWh/yr`;
    document.getElementById("card-emissions-value").textContent = emissionsFmt.value;
    document.getElementById("card-emissions-unit").textContent = `${emissionsFmt.unit} MT CO2`;
    document.getElementById("card-money-value").textContent = `$${moneyFmt.value}`;
    document.getElementById("card-money-unit").textContent = `${moneyFmt.unit}/yr`;
  }

  slider.addEventListener("input", (e) => render(Number(e.target.value)));
  render(Number(slider.value));
}