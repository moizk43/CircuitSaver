"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, DollarSign, Wind, Home } from "lucide-react";

const TOTAL_HOMES_WORLD = 2_100_000_000;
const ENERGY_PER_HOME_MWH = 10.5;
const COST_PER_MWH = 148;
const EMISSIONS_PER_MWH_KG = 386;

function calcMetrics(pct: number) {
  const homes = Math.round((pct / 100) * TOTAL_HOMES_WORLD);
  const energyMWh = Math.round(homes * ENERGY_PER_HOME_MWH);
  const moneySaved = Math.round(energyMWh * COST_PER_MWH);
  const emissionsKg = Math.round(energyMWh * EMISSIONS_PER_MWH_KG);
  return { homes, energyMWh, moneySaved, emissionsKg };
}

const STEPS = [0, 5, 10, 25, 50, 75, 100];

export default function ImpactSlider() {
  const [pct, setPct] = useState(10);
  const metrics = calcMetrics(pct);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setPct(Number(e.target.value));
  }, []);

  function formatLarge(n: number): { value: string; unit: string } {
    if (n >= 1_000_000_000)
      return { value: (n / 1_000_000_000).toFixed(2), unit: "B" };
    if (n >= 1_000_000)
      return { value: (n / 1_000_000).toFixed(1), unit: "M" };
    if (n >= 1_000)
      return { value: (n / 1_000).toFixed(1), unit: "K" };
    return { value: String(n), unit: "" };
  }

  const homeFmt = formatLarge(metrics.homes);
  const moneyFmt = formatLarge(metrics.moneySaved);
  const energyFmt = formatLarge(metrics.energyMWh);
  const emissionsFmt = formatLarge(metrics.emissionsKg / 1000);

  const trackStyle = {
    background: `linear-gradient(to right, #56d16d ${pct}%, #e5e7eb ${pct}%)`,
  };

  return (
    <section
      className="relative py-24 px-6 bg-mesh overflow-hidden"
      aria-labelledby="impact-heading"
    >
      <div className="absolute top-10 left-1/4 w-72 h-72 rounded-full
                      bg-brand-100/40 blur-3xl -z-10 animate-float" />
      <div className="absolute bottom-10 right-1/4 w-56 h-56 rounded-full
                      bg-brand-200/30 blur-3xl -z-10 animate-float"
           style={{ animationDelay: "3s" }} />

      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center mb-12"
        >
          <span className="inline-block px-4 py-1.5 rounded-full text-sm font-semibold
                           bg-brand-100 text-brand-700 mb-4">
            Real-World Impact
          </span>
          <h2
            id="impact-heading"
            className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
          >
            What if{" "}
            <span className="text-gradient">{pct}%</span>
            {" "}of homes used Verdant?
          </h2>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            Drag the slider to explore the global impact of clean energy adoption.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="mb-4 px-2"
        >
          <div className="flex justify-between text-xs text-gray-400 mb-2 font-medium">
            {STEPS.map((s) => (
              <span key={s}>{s}%</span>
            ))}
          </div>
          <input
            type="range"
            min={0}
            max={100}
            step={1}
            value={pct}
            onChange={handleChange}
            style={trackStyle}
            className="w-full h-1.5 rounded-full cursor-pointer"
            aria-label="Percentage of homes using Verdant"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={pct}
          />
          <div className="flex justify-between mt-1">
            <span className="text-xs text-gray-400">0 homes</span>
            <span className="text-xs text-gray-400">2.1B homes</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.25 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-10"
        >
          {[
            {
              icon: <Home className="text-brand-500" size={22} />,
              label: "Homes Powered",
              value: homeFmt.value,
              unit: homeFmt.unit,
              bg: "bg-brand-50",
            },
            {
              icon: <Zap className="text-amber-500" size={22} />,
              label: "Energy Saved",
              value: energyFmt.value,
              unit: `${energyFmt.unit} MWh/yr`,
              bg: "bg-amber-50",
            },
            {
              icon: <Wind className="text-sky-500" size={22} />,
              label: "Emissions Reduced",
              value: emissionsFmt.value,
              unit: `${emissionsFmt.unit} MT CO₂`,
              bg: "bg-sky-50",
            },
            {
              icon: <DollarSign className="text-emerald-500" size={22} />,
              label: "Money Saved",
              value: `$${moneyFmt.value}`,
              unit: `${moneyFmt.unit}/yr`,
              bg: "bg-emerald-50",
            },
          ].map((card, i) => (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
              whileHover={{ y: -4 }}
              className={`${card.bg} rounded-3xl p-5 border border-white shadow-sm`}
            >
              <div className="mb-3">{card.icon}</div>
              <AnimatePresence mode="wait">
                <motion.div
                  key={card.value + card.unit}
                  initial={{ opacity: 0.6, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <p className="text-2xl font-bold text-gray-900 leading-none">
                    {card.value}
                    <span className="text-base font-semibold ml-1 text-gray-500">
                      {card.unit}
                    </span>
                  </p>
                </motion.div>
              </AnimatePresence>
              <p className="text-xs text-gray-500 mt-1.5 font-medium">{card.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
