"use client";

import { motion } from "framer-motion";
import { twMerge } from "tailwind-merge";
import { clsx } from "clsx";
import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
  hover?: boolean;
  padding?: "sm" | "md" | "lg";
}

const paddingMap = { sm: "p-4", md: "p-6", lg: "p-8" };

export default function Card({
  glass = false,
  hover = true,
  padding = "md",
  className,
  children,
  ...props
}: CardProps) {
  return (
    <motion.div
      whileHover={hover ? { y: -3, boxShadow: "0 20px 40px rgba(0,0,0,0.08)" } : {}}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={twMerge(
        clsx(
          "rounded-3xl border border-gray-100 shadow-sm",
          "transition-shadow duration-300",
          glass
            ? "glass"
            : "bg-white",
          paddingMap[padding],
          className
        )
      )}
      {...(props as any)}
    >
      {children}
    </motion.div>
  );
}
