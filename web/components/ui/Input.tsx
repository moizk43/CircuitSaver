"use client";

import { forwardRef, InputHTMLAttributes, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import { twMerge } from "tailwind-merge";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, type, id, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === "password";
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="flex flex-col gap-1.5 w-full">
        <label
          htmlFor={inputId}
          className="text-sm font-semibold text-gray-700"
        >
          {label}
        </label>
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            type={isPassword && showPassword ? "text" : type}
            aria-describedby={
              error
                ? `${inputId}-error`
                : hint
                ? `${inputId}-hint`
                : undefined
            }
            aria-invalid={!!error}
            className={twMerge(
              clsx(
                "w-full rounded-2xl border px-4 py-3 text-base font-medium",
                "bg-white/80 backdrop-blur-sm transition-all duration-200",
                "placeholder:text-gray-400 focus:outline-none focus-visible:ring-2",
                "focus-visible:ring-brand-500 focus-visible:ring-offset-1",
                error
                  ? "border-red-400 bg-red-50/40 focus-visible:ring-red-400"
                  : "border-gray-200 hover:border-gray-300 focus:border-brand-400",
                isPassword ? "pr-12" : "",
                className
              )
            )}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400
                         hover:text-gray-600 transition-colors focus:outline-none
                         focus-visible:text-brand-500"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          )}
        </div>
        <AnimatePresence mode="wait">
          {error ? (
            <motion.p
              key="error"
              id={`${inputId}-error`}
              role="alert"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
              className="text-sm text-red-500 font-medium flex items-center gap-1"
            >
              <span aria-hidden="true">✕</span> {error}
            </motion.p>
          ) : hint ? (
            <p id={`${inputId}-hint`} className="text-xs text-gray-400">
              {hint}
            </p>
          ) : null}
        </AnimatePresence>
      </div>
    );
  }
);

Input.displayName = "Input";
export default Input;
