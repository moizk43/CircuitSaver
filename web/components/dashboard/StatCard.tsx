"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import AnimatedCounter from "../ui/AnimatedCounter";

interface StatCardProps {
  title: string;
  subtitle?: string;
  value: number;
  prefix?: string;
  suffix?: string;
  unit?: string;
  unitDisplay?: ReactNode;
  description?: string;
  icon?: ReactNode;
  color?: string;
  delay?: number;
}

export default function StatCard({
  title,
  subtitle,
  value,
  prefix = "",
  suffix = "",
  unit,
  unitDisplay,
  description,
  icon,
  color = "text-brand-500",
  delay = 0,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 28, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.65,
        delay,
        type: "spring",
        stiffness: 120,
        damping: 18,
      }}
      whileHover={{ y: -5 }}
      className="relative bg-white rounded-3xl border border-gray-100
                 shadow-sm hover:shadow-lg transition-shadow duration-300
                 p-8 flex flex-col justify-between overflow-hidden group"
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100
                   transition-opacity duration-500 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at top right, rgba(86,209,109,0.05), transparent 70%)",
        }}
      />

      <div className="relative">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">
              {title}
            </p>
            {subtitle && (
              <p className="text-xs text-gray-400">{subtitle}</p>
            )}
          </div>
          {icon && (
            <div
              className={`w-11 h-11 rounded-2xl bg-gray-50 flex items-center
                         justify-center ${color} border border-gray-100`}
            >
              {icon}
            </div>
          )}
        </div>

        <div className="mt-2">
          <span className={`text-4xl md:text-5xl font-extrabold ${color} leading-none`}>
            <AnimatedCounter
              to={value}
              prefix={prefix}
              suffix={suffix}
              duration={2200}
              separator=","
            />
          </span>
          {unit && (
            <span className="text-lg font-semibold text-gray-400 ml-2">
              {unit}
            </span>
          )}
          {unitDisplay && (
            <div className="mt-1">{unitDisplay}</div>
          )}
        </div>

        {description && (
          <p className="text-sm text-gray-400 mt-3 leading-relaxed">
            {description}
          </p>
        )}
      </div>
    </motion.div>
  );
}
