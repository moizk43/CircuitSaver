"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  alpha: number;
  size: number;
  life: number;
  maxLife: number;
}

export default function Globe() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>();
  const rotationRef = useRef(0);
  const particlesRef = useRef<Particle[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const SIZE = 420;
    canvas.width = SIZE;
    canvas.height = SIZE;
    const cx = SIZE / 2;
    const cy = SIZE / 2;
    const R = 160;

    function spawnParticle() {
      const angle = Math.random() * Math.PI * 2;
      const r = R + (Math.random() - 0.5) * 30;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      const speed = 0.2 + Math.random() * 0.4;
      const tangentAngle = angle + Math.PI / 2 + (Math.random() - 0.5) * 0.6;
      particlesRef.current.push({
        x,
        y,
        vx: speed * Math.cos(tangentAngle),
        vy: speed * Math.sin(tangentAngle),
        alpha: 1,
        size: 1.5 + Math.random() * 2,
        life: 0,
        maxLife: 60 + Math.random() * 80,
      });
    }

    function drawGlobe(rot: number) {
      const glow = ctx!.createRadialGradient(cx, cy, R * 0.5, cx, cy, R * 1.4);
      glow.addColorStop(0, "rgba(86,209,109,0.06)");
      glow.addColorStop(0.7, "rgba(86,209,109,0.03)");
      glow.addColorStop(1, "rgba(86,209,109,0)");
      ctx!.fillStyle = glow;
      ctx!.beginPath();
      ctx!.arc(cx, cy, R * 1.4, 0, Math.PI * 2);
      ctx!.fill();

      const grad = ctx!.createRadialGradient(
        cx - R * 0.3,
        cy - R * 0.3,
        R * 0.1,
        cx,
        cy,
        R
      );
      grad.addColorStop(0, "#f0fdf4");
      grad.addColorStop(0.5, "#dcfce7");
      grad.addColorStop(1, "#bbf7d0");
      ctx!.beginPath();
      ctx!.arc(cx, cy, R, 0, Math.PI * 2);
      ctx!.fillStyle = grad;
      ctx!.fill();

      ctx!.save();
      ctx!.beginPath();
      ctx!.arc(cx, cy, R, 0, Math.PI * 2);
      ctx!.clip();

      ctx!.strokeStyle = "rgba(86,209,109,0.18)";
      ctx!.lineWidth = 0.8;
      for (let i = 0; i < 12; i++) {
        const theta = (i / 12) * Math.PI * 2 + rot;
        ctx!.beginPath();
        for (let lat = -Math.PI / 2; lat <= Math.PI / 2; lat += 0.05) {
          const projX = cx + R * Math.cos(lat) * Math.cos(theta);
          const projY = cy + R * Math.sin(lat);
          if (lat === -Math.PI / 2) ctx!.moveTo(projX, projY);
          else ctx!.lineTo(projX, projY);
        }
        ctx!.stroke();
      }

      for (let j = 1; j < 6; j++) {
        const phi = (j / 6) * Math.PI - Math.PI / 2;
        const r2 = Math.abs(R * Math.cos(phi));
        const yOff = cy + R * Math.sin(phi);
        ctx!.beginPath();
        ctx!.arc(cx, yOff, r2, 0, Math.PI * 2);
        ctx!.stroke();
      }

      ctx!.restore();

      ctx!.beginPath();
      ctx!.arc(cx, cy, R, 0, Math.PI * 2);
      ctx!.strokeStyle = "rgba(86,209,109,0.35)";
      ctx!.lineWidth = 1.5;
      ctx!.stroke();

      const spec = ctx!.createRadialGradient(
        cx - R * 0.38,
        cy - R * 0.38,
        2,
        cx - R * 0.2,
        cy - R * 0.2,
        R * 0.55
      );
      spec.addColorStop(0, "rgba(255,255,255,0.55)");
      spec.addColorStop(1, "rgba(255,255,255,0)");
      ctx!.beginPath();
      ctx!.arc(cx, cy, R, 0, Math.PI * 2);
      ctx!.fillStyle = spec;
      ctx!.fill();
    }

    function drawParticles() {
      particlesRef.current.forEach((p) => {
        const a = p.alpha * (1 - p.life / p.maxLife);
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(86,209,109,${a * 0.8})`;
        ctx!.fill();

        const pg = ctx!.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 3);
        pg.addColorStop(0, `rgba(86,209,109,${a * 0.3})`);
        pg.addColorStop(1, "rgba(86,209,109,0)");
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
        ctx!.fillStyle = pg;
        ctx!.fill();
      });
    }

    function animate() {
      ctx!.clearRect(0, 0, SIZE, SIZE);

      rotationRef.current += 0.004;
      drawGlobe(rotationRef.current);

      if (Math.random() < 0.3) spawnParticle();

      particlesRef.current = particlesRef.current.filter((p) => {
        p.life++;
        p.x += p.vx;
        p.y += p.vy;
        return p.life < p.maxLife;
      });
      drawParticles();

      animRef.current = requestAnimationFrame(animate);
    }

    animate();
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
      className="relative flex items-center justify-center"
      aria-hidden="true"
    >
      <div className="absolute inset-0 rounded-full bg-brand-100/30 blur-3xl scale-125" />
      <canvas
        ref={canvasRef}
        className="relative z-10 max-w-full"
        style={{ width: 340, height: 340 }}
      />
    </motion.div>
  );
}
