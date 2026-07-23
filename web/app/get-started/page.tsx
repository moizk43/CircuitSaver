"use client";

import { useState, useRef, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, ArrowRight } from "lucide-react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { createUser, userExists } from "@/lib/users";
import { setSession } from "@/lib/auth";

interface FormErrors {
  username?: string;
  password?: string;
  confirm?: string;
}

export default function GetStartedPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const usernameRef = useRef<HTMLInputElement>(null);

  function validate(): FormErrors {
    const e: FormErrors = {};
    if (!username.trim()) {
      e.username = "Username is required.";
    } else if (username.trim().length < 3) {
      e.username = "Username must be at least 3 characters.";
    } else if (userExists(username.trim())) {
      e.username = "That username is already taken.";
    }
    if (!password) {
      e.password = "Password is required.";
    } else if (password.length < 8) {
      e.password = "Password must be at least 8 characters.";
    }
    if (!confirm) {
      e.confirm = "Please confirm your password.";
    } else if (password !== confirm) {
      e.confirm = "Passwords do not match.";
    }
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
    await new Promise((r) => setTimeout(r, 700));
    createUser(username.trim(), password);
    setSession(username.trim());
    setSuccess(true);
    setTimeout(() => router.push("/dashboard"), 1200);
  }

  return (
    <div
      className="min-h-screen bg-mesh flex items-center justify-center px-6 py-16"
    >
      <div className="fixed top-0 right-0 w-96 h-96 rounded-full
                      bg-brand-100/30 blur-3xl -z-10" />
      <div className="fixed bottom-0 left-0 w-72 h-72 rounded-full
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
                     focus-visible:ring-2 focus-visible:ring-brand-500 rounded-xl w-fit mx-auto"
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
          <AnimatePresence mode="wait">
            {success ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center py-8 text-center gap-4"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                >
                  <CheckCircle2
                    size={56}
                    className="text-brand-500"
                    aria-hidden="true"
                  />
                </motion.div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Welcome to Verdant!
                </h2>
                <p className="text-gray-500">
                  Your account has been created. Redirecting you now…
                </p>
              </motion.div>
            ) : (
              <motion.div key="form" initial={{ opacity: 1 }}>
                <div className="mb-8">
                  <h1 className="text-2xl font-extrabold text-gray-900 mb-1">
                    Create your account
                  </h1>
                  <p className="text-gray-500 text-sm">
                    Join Verdant and start saving energy today.
                  </p>
                </div>

                <form
                  onSubmit={handleSubmit}
                  className="flex flex-col gap-5"
                  noValidate
                >
                  <Input
                    ref={usernameRef}
                    label="Username"
                    type="text"
                    placeholder="e.g. johndoe"
                    value={username}
                    onChange={(e) => {
                      setUsername(e.target.value);
                      if (errors.username)
                        setErrors((prev) => ({ ...prev, username: undefined }));
                    }}
                    error={errors.username}
                    autoComplete="username"
                    autoFocus
                  />
                  <Input
                    label="Password"
                    type="password"
                    placeholder="Min. 8 characters"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errors.password)
                        setErrors((prev) => ({ ...prev, password: undefined }));
                    }}
                    error={errors.password}
                    autoComplete="new-password"
                    hint="At least 8 characters"
                  />
                  <Input
                    label="Confirm Password"
                    type="password"
                    placeholder="Repeat your password"
                    value={confirm}
                    onChange={(e) => {
                      setConfirm(e.target.value);
                      if (errors.confirm)
                        setErrors((prev) => ({ ...prev, confirm: undefined }));
                    }}
                    error={errors.confirm}
                    autoComplete="new-password"
                  />

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    fullWidth
                    loading={loading}
                    className="mt-2"
                  >
                    Create Account
                    <ArrowRight size={18} aria-hidden="true" />
                  </Button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-6">
                  Already have an account?{" "}
                  <Link
                    href="/sign-in"
                    className="text-brand-600 font-semibold hover:underline
                               focus:outline-none focus-visible:ring-2
                               focus-visible:ring-brand-500 rounded"
                  >
                    Sign in
                  </Link>
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
