# Verdant

A premium, investor-ready frontend for a clean-energy startup, built with Next.js 14, TypeScript, TailwindCSS, and Framer Motion.

## Setup

```bash
npm install
npm run dev
```

Visit http://localhost:3000

## Notes

- Mock authentication is stored in the browser's localStorage (see `lib/users.ts`) and is designed to be swapped for Supabase, Firebase, Clerk, or Auth0 with minimal changes.
- Sessions are stored in sessionStorage (see `lib/auth.ts`).
- To use your own logo, place `logo.png` in `/public/` and swap the inline SVG in `app/dashboard/page.tsx` and `components/layout/Navbar.tsx` with a Next.js `<Image>` component.
