"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, useScroll } from "framer-motion";
import { Menu, X } from "lucide-react";
import Button from "../ui/Button";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();

  useEffect(() => {
    return scrollY.on("change", (y) => setScrolled(y > 20));
  }, [scrollY]);

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/80 backdrop-blur-xl shadow-sm border-b border-gray-100"
          : "bg-transparent"
      }`}
    >
      <nav
        className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between"
        aria-label="Main navigation"
      >
        <Link
          href="/"
          className="flex items-center gap-3 group focus:outline-none
                     focus-visible:ring-2 focus-visible:ring-brand-500 rounded-xl"
          aria-label="Verdant home"
        >
          <motion.div
            whileHover={{ rotate: 5, scale: 1.08 }}
            transition={{ type: "spring", stiffness: 400 }}
            className="w-9 h-9 rounded-xl bg-brand-500 flex items-center
                       justify-center shadow-lg shadow-brand-500/30"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
              <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
            </svg>
          </motion.div>
          <span className="text-xl font-bold tracking-tight text-gray-900 group-hover:text-brand-600 transition-colors">
            Verdant
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-3">
          <Link href="/sign-in">
            <Button variant="ghost" size="sm">
              Sign In
            </Button>
          </Link>
          <Link href="/get-started">
            <Button variant="primary" size="sm">
              Get Started
            </Button>
          </Link>
        </div>

        <button
          className="md:hidden rounded-xl p-2 text-gray-600 hover:bg-gray-100
                     focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 transition-colors"
          onClick={() => setMenuOpen((v) => !v)}
          aria-expanded={menuOpen}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {menuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="md:hidden bg-white/95 backdrop-blur-xl border-t border-gray-100
                     px-6 py-4 flex flex-col gap-3 shadow-lg"
        >
          <Link href="/sign-in" onClick={() => setMenuOpen(false)}>
            <Button variant="ghost" size="md" fullWidth>
              Sign In
            </Button>
          </Link>
          <Link href="/get-started" onClick={() => setMenuOpen(false)}>
            <Button variant="primary" size="md" fullWidth>
              Get Started
            </Button>
          </Link>
        </motion.div>
      )}
    </motion.header>
  );
}
