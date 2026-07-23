"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  DollarSign,
  Zap,
  Battery,
  Wind,
  LogOut,
  Home,
} from "lucide-react";
import { getSession, clearSession } from "@/lib/auth";
import StatCard from "@/components/dashboard/StatCard";
import Button from "@/components/ui/Button";
import AnimatedCounter from "@/components/ui/AnimatedCounter";

export default function DashboardPage() {
  const router = useRouter();
  const [username, setUsername] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.replace("/sign-in");
      return;
    }
    setUsername(session.username);
    setMounted(true);
  }, [router]);

  function handleSignOut() {
    clearSession();
    router.push("/");
  }

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-gray-50/50 bg-mesh">
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl
                   border-b border-gray-100 shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center
                        justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center
                           justify-center shadow-lg shadow-brand-500/30">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                   stroke="white" strokeWidth="2.2" strokeLinecap="round"
                   strokeLinejoin="round" aria-hidden="true">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
              </svg>
            </div>
            <span className="font-bold text-lg text-gray-900">Verdant</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="hidden sm:block text-sm text-gray-500 font-medium">
              Welcome back,{" "}
              <span className="text-gray-800 font-semibold">{username}</span>
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSignOut}
              aria-label="Sign out"
            >
              <LogOut size={16} aria-hidden="true" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </motion.header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <p className="text-sm font-semibold text-brand-500 uppercase
                        tracking-widest mb-2">
            Dashboard
          </p>
          <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">
            Your Impact
          </h1>
          <p className="text-gray-500 text-lg">
            Here&rsquo;s how Verdant is working for you.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.88 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, type: "spring", stiffness: 80, delay: 0.1 }}
          className="flex flex-col items-center justify-center my-10 mb-16"
        >
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-brand-300/30
                            blur-2xl scale-150 animate-pulse-soft" />
            <div className="relative w-28 h-28 md:w-36 md:h-36 rounded-3xl
                            bg-gradient-to-br from-brand-400 to-brand-600
                            shadow-2xl shadow-brand-500/40 flex items-center
                            justify-center">
              {/*
                To use your own logo:
                import Image from "next/image";
                <Image src="/logo.png" alt="Verdant logo" width={80} height={80} />
              */}
              <svg
                width="60"
                height="60"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-label="Verdant logo"
                role="img"
              >
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
              </svg>
            </div>
          </div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-5 text-2xl font-extrabold text-gray-900 tracking-tight"
          >
            Verdant
          </motion.p>
          <p className="text-brand-500 font-semibold text-sm mt-1">
            Clean energy, intelligently delivered.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <StatCard
            title="Money Saved"
            subtitle="Total savings this year"
            value={14328}
            prefix="$"
            description="Compared to average grid pricing in your region."
            icon={<DollarSign size={22} />}
            color="text-emerald-500"
            delay={0.15}
          />

          <motion.div
            initial={{ opacity: 0, y: 28, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              duration: 0.65,
              delay: 0.25,
              type: "spring",
              stiffness: 120,
              damping: 18,
            }}
            whileHover={{ y: -5 }}
            className="relative bg-white rounded-3xl border border-gray-100
                       shadow-sm hover:shadow-lg transition-shadow duration-300
                       p-8 overflow-hidden group"
          >
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100
                           transition-opacity duration-500 pointer-events-none"
                 style={{
                   background:
                     "radial-gradient(ellipse at top right, rgba(245,158,11,0.05), transparent 70%)",
                 }}
            />
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm font-semibold text-gray-500 uppercase
                              tracking-wider mb-1">
                  Energy Comparison
                </p>
                <p className="text-xs text-gray-400">
                  Equivalent impact, visualized
                </p>
              </div>
              <div className="w-11 h-11 rounded-2xl bg-amber-50 flex items-center
                             justify-center text-amber-500 border border-gray-100">
                <Zap size={22} aria-hidden="true" />
              </div>
            </div>
            <p className="text-gray-500 text-sm mb-3">
              Enough energy to power
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-extrabold text-amber-500">
                <AnimatedCounter to={842} duration={2200} />
              </span>
              <span className="text-xl font-bold text-gray-700">homes</span>
            </div>
            <p className="text-gray-400 text-sm mt-1">for an entire day</p>
            <div className="flex items-center gap-1.5 mt-4">
              {Array.from({ length: 12 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: 0.4 + i * 0.05, duration: 0.4 }}
                  className={`rounded-full w-2 ${
                    i < 10 ? "bg-amber-400" : "bg-gray-200"
                  }`}
                  style={{ height: `${12 + Math.sin(i) * 8}px` }}
                />
              ))}
              <Home size={14} className="text-amber-400 ml-1" aria-hidden="true" />
            </div>
          </motion.div>

          <StatCard
            title="Energy Saved"
            subtitle="Cumulative MWh delivered"
            value={487}
            suffix=" MWh"
            description="Clean energy fed back into the grid or stored locally."
            icon={<Battery size={22} />}
            color="text-brand-500"
            delay={0.35}
          />

          <motion.div
            initial={{ opacity: 0, y: 28, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              duration: 0.65,
              delay: 0.45,
              type: "spring",
              stiffness: 120,
              damping: 18,
            }}
            whileHover={{ y: -5 }}
            className="relative bg-white rounded-3xl border border-gray-100
                       shadow-sm hover:shadow-lg transition-shadow duration-300
                       p-8 overflow-hidden group"
          >
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100
                           transition-opacity duration-500 pointer-events-none"
                 style={{
                   background:
                     "radial-gradient(ellipse at top right, rgba(14,165,233,0.05), transparent 70%)",
                 }}
            />
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm font-semibold text-gray-500 uppercase
                              tracking-wider mb-1">
                  Emissions Reduced
                </p>
                <p className="text-xs text-gray-400">CO₂ equivalent prevented</p>
              </div>
              <div className="w-11 h-11 rounded-2xl bg-sky-50 flex items-center
                             justify-center text-sky-500 border border-gray-100">
                <Wind size={22} aria-hidden="true" />
              </div>
            </div>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-5xl font-extrabold text-sky-500">
                <AnimatedCounter to={128} duration={2000} />
              </span>
              <span className="text-lg font-bold text-gray-700">
                Metric Tons
              </span>
            </div>
            <p className="text-gray-500 text-sm font-medium">
              CO₂ Prevented
            </p>
            <p className="text-gray-400 text-xs mt-2 leading-relaxed">
              Equivalent to planting{" "}
              <span className="text-sky-600 font-semibold">
                <AnimatedCounter to={5842} duration={2400} /> trees
              </span>{" "}
              this year.
            </p>

            <div className="mt-4 flex items-end gap-1.5">
              {[30, 48, 42, 65, 72, 60, 88, 95, 82, 100, 92, 128].map(
                (v, i) => (
                  <motion.div
                    key={i}
                    initial={{ scaleY: 0 }}
                    animate={{ scaleY: 1 }}
                    transition={{ delay: 0.5 + i * 0.05, duration: 0.4 }}
                    className="flex-1 rounded-t-sm bg-sky-200 hover:bg-sky-400
                               transition-colors duration-200"
                    style={{ height: `${(v / 128) * 40}px` }}
                    title={`Month ${i + 1}: ${v} MT`}
                  />
                )
              )}
            </div>
            <p className="text-xs text-gray-400 mt-1">Monthly CO₂ trend (MT)</p>
          </motion.div>
        </div>

        <div className="h-16" />
      </main>
    </div>
  );
}
