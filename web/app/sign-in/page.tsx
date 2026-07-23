"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, AlertCircle } from "lucide-react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { validateUser } from "@/lib/users";
import { setSession } from "@/lib/auth";

interface FormErrors {
  username?: string;
  password?: string;
  general?: string;
}

export default function SignInPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  function validate(): FormErrors {
    const e: FormErrors = {};
    if (!username.trim()) e.username = "Username is required.";
    if (!password) e.password = "Password is required.";
    return e;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setErrors({});
    setLoading(true);
    await new Promise((r) => setTimeout(r, 600));
    const valid = validateUser(username.trim(), password);
    if (valid) {
      setSession(username.trim());
      router.push("/dashboard");
    } else {
      setLoading(false);
      setErrors({ general: "Incorrect username or password. Please try again." });
    }
  }

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-6 py-16">
      <div className="fixed top-0 left-0 w-96 h-96 rounded-full
                      bg-brand-100/30 blur-3xl -z-10" />
      <div className="fixed bottom-0 right-0 w-72 h-72 rounded-full
                      bg-brand-200/20 blur-3xl -z-10" />

      <motion.div
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, type: "spring", stiffness: 100 }}
        className="w-full max-w-md"
      >
        <Link
          href="/"
          className="flex items-center gap-2 mb-8 focus:outline-none
                     focus-visible:ring-2 focus-visible:ring-brand-500
                     rounded-xl w-fit mx-auto"
        >
          <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center
                         justify-center shadow-lg shadow-brand-500/30">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                 stroke="white" strokeWidth="2.2" strokeLinecap="round"
                 strokeLinejoin="round" aria-hidden="true">
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
              <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
            </svg>
          </div>
          <span className="text-xl font-bold text-gray-900">Verdant</span>
        </Link>

        <div className="bg-white/90 backdrop-blur-xl rounded-3xl border
                        border-gray-100 shadow-xl shadow-gray-200/50 p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-extrabold text-gray-900 mb-1">
              Welcome back
            </h1>
            <p className="text-gray-500 text-sm">Sign in to your Verdant account.</p>
          </div>

          <AnimatePresence>
            {errors.general && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8 }}
                role="alert"
                className="flex items-center gap-3 bg-red-50 border border-red-200
                           rounded-2xl px-4 py-3 mb-5 text-sm text-red-600"
              >
                <AlertCircle size={18} className="shrink-0" aria-hidden="true" />
                {errors.general}
              </motion.div>
            )}
          </AnimatePresence>

          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-5"
            noValidate
          >
            <Input
              label="Username"
              type="text"
              placeholder="Your username"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setErrors((prev) => ({
                  ...prev,
                  username: undefined,
                  general: undefined,
                }));
              }}
              error={errors.username}
              autoComplete="username"
              autoFocus
            />
            <Input
              label="Password"
              type="password"
              placeholder="Your password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setErrors((prev) => ({
                  ...prev,
                  password: undefined,
                  general: undefined,
                }));
              }}
              error={errors.password}
              autoComplete="current-password"
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              loading={loading}
              className="mt-2"
            >
              Sign In
              <ArrowRight size={18} aria-hidden="true" />
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Don&rsquo;t have an account?{" "}
            <Link
              href="/get-started"
              className="text-brand-600 font-semibold hover:underline
                         focus:outline-none focus-visible:ring-2
                         focus-visible:ring-brand-500 rounded"
            >
              Get started free
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
