"use client";

import { motion } from "framer-motion";
import { Leaf, Zap, Globe2, Heart } from "lucide-react";
import Card from "../ui/Card";

const pillars = [
  {
    icon: <Leaf size={24} />,
    title: "Built for sustainability",
    description:
      "Every product decision is made with long-term environmental impact in mind. We optimize for the planet, not just profit.",
    color: "text-brand-500",
    bg:   "bg-brand-50",
  },
  {
    icon: <Zap size={24} />,
    title: "Smarter energy",
    description:
      "Proprietary AI algorithms monitor, predict, and optimize home energy consumption in real time — automatically.",
    color: "text-amber-500",
    bg:   "bg-amber-50",
  },
  {
    icon: <Globe2 size={24} />,
    title: "Globally accessible",
    description:
      "From rural communities to urban centers, Verdant is designed to work anywhere electricity reaches.",
    color: "text-sky-500",
    bg:   "bg-sky-50",
  },
  {
    icon: <Heart size={24} />,
    title: "Human-centered",
    description:
      "Clean technology should never feel complicated. Verdant is invisible when it works and clear when you need it.",
    color: "text-rose-400",
    bg:   "bg-rose-50",
  },
];

export default function MissionSection() {
  return (
    <section
      id="mission"
      className="py-28 px-6 bg-white"
      aria-labelledby="mission-heading"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-3xl mx-auto text-center mb-20"
        >
          <span className="inline-block px-4 py-1.5 rounded-full text-sm font-semibold
                           bg-brand-100 text-brand-700 mb-5">
            Our Mission
          </span>
          <h2
            id="mission-heading"
            className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-6
                       leading-tight tracking-tight"
          >
            Accelerating the world&rsquo;s transition to
            <span className="text-gradient"> clean energy</span>
          </h2>
          <p className="text-xl text-gray-500 leading-relaxed">
            We exist because the climate crisis is urgent and the solutions
            available to ordinary homeowners have been too complicated, too
            expensive, or too inaccessible. Verdant changes that.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {pillars.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.6 }}
            >
              <Card padding="lg" className="h-full">
                <div
                  className={`w-12 h-12 rounded-2xl ${p.bg} ${p.color}
                              flex items-center justify-center mb-5`}
                >
                  {p.icon}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {p.title}
                </h3>
                <p className="text-gray-500 leading-relaxed text-sm">
                  {p.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-20 rounded-3xl bg-gradient-to-r from-brand-500 to-brand-600
                     p-10 flex flex-col md:flex-row items-center justify-between
                     gap-8 text-white shadow-xl shadow-brand-500/20"
        >
          {[
            { value: "2.4M+", label: "Homes connected" },
            { value: "487K MWh", label: "Clean energy delivered" },
            { value: "$214M", label: "Saved by homeowners" },
            { value: "128K MT", label: "CO₂ prevented" },
          ].map((stat) => (
            <div key={stat.label} className="text-center md:text-left">
              <p className="text-3xl md:text-4xl font-extrabold mb-1">
                {stat.value}
              </p>
              <p className="text-brand-100 text-sm font-medium">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
