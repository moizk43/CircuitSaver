"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Globe from "./Globe";
import Button from "../ui/Button";
import { ArrowRight, ChevronDown } from "lucide-react";

export default function HeroSection() {
  return (
    <section
      className="relative min-h-screen flex flex-col items-center justify-center
                 px-6 pt-20 pb-16 overflow-hidden bg-white"
      aria-labelledby="hero-heading"
    >
      <div className="absolute inset-0 bg-mesh -z-10" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px]
                      rounded-full bg-brand-100/25 blur-3xl -z-10" />

      <div className="max-w-7xl w-full mx-auto grid lg:grid-cols-2 gap-16
                      items-center">
        <div className="order-2 lg:order-1 text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full
                             bg-brand-100 text-brand-700 text-sm font-semibold mb-6">
              <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse-soft" />
              The Future of Home Energy
            </span>
          </motion.div>

          <motion.h1
            id="hero-heading"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-5xl md:text-6xl lg:text-7xl font-extrabold
                       leading-[1.08] tracking-tight text-gray-900 mb-6"
          >
            Clean energy,{" "}
            <span className="text-gradient block">intelligently</span>
            delivered.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.35 }}
            className="text-lg md:text-xl text-gray-500 leading-relaxed
                       max-w-xl mx-auto lg:mx-0 mb-10"
          >
            Verdant makes clean, sustainable energy accessible to every home on
            the planet — reducing emissions, lowering bills, and powering a
            greener future.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
          >
            <Link href="/get-started">
              <Button size="lg" variant="primary">
                Get Started Free
                <ArrowRight size={18} aria-hidden="true" />
              </Button>
            </Link>
            <Link href="/sign-in">
              <Button size="lg" variant="secondary">
                Sign In
              </Button>
            </Link>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-sm text-gray-400 mt-8"
          >
            Trusted by homeowners across{" "}
            <span className="text-brand-600 font-semibold">42 countries</span>
          </motion.p>
        </div>

        <div className="order-1 lg:order-2 flex justify-center lg:justify-end">
          <Globe />
        </div>
      </div>

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        onClick={() =>
          document
            .getElementById("mission")
            ?.scrollIntoView({ behavior: "smooth" })
        }
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col
                   items-center gap-1 text-gray-400 hover:text-brand-500
                   transition-colors focus:outline-none
                   focus-visible:ring-2 focus-visible:ring-brand-500 rounded-lg p-2"
        aria-label="Scroll to mission section"
      >
        <span className="text-xs font-medium">Scroll</span>
        <motion.div
          animate={{ y: [0, 5, 0] }}
          transition={{ repeat: Infinity, duration: 1.8, ease: "easeInOut" }}
        >
          <ChevronDown size={18} />
        </motion.div>
      </motion.button>
    </section>
  );
}
