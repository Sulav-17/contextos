"use client";

import { useEffect, useRef } from "react";

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  drift: number;
  opacity: number;
  radius: number;
  life: number;
  maxLife: number;
  tone: number;
};

type PointerState = {
  active: boolean;
  x: number;
  y: number;
  lastX: number;
  lastY: number;
  lastTrailAt: number;
};

type Palette = {
  background: string;
  particle: string[];
  connection: string;
  trail: string;
};

const DESKTOP_MIN_PARTICLES = 28;
const DESKTOP_MAX_PARTICLES = 56;
const MOBILE_MIN_PARTICLES = 8;
const MOBILE_MAX_PARTICLES = 16;
const MAX_CONNECTIONS_DESKTOP = 36;
const MAX_CONNECTIONS_MOBILE = 8;
const FRAME_INTERVAL_MS = 1000 / 30;
const RESIZE_DEBOUNCE_MS = 140;

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function getPalette(): Palette {
  if (document.documentElement.dataset.theme === "light") {
    return {
      background: "rgba(251, 246, 234, 0.05)",
      particle: [
        "rgba(226, 143, 20, 0.96)",
        "rgba(155, 88, 12, 0.82)",
        "rgba(255, 198, 70, 0.9)",
        "rgba(22, 142, 166, 0.34)",
      ],
      connection: "rgba(150, 86, 11, 0.48)",
      trail: "rgba(226, 139, 18, 0.88)",
    };
  }

  return {
    background: "rgba(5, 9, 18, 0.08)",
    particle: [
      "rgba(87, 219, 246, 0.84)",
      "rgba(86, 216, 190, 0.68)",
      "rgba(153, 147, 255, 0.68)",
      "rgba(223, 244, 255, 0.78)",
    ],
    connection: "rgba(91, 211, 246, 0.28)",
    trail: "rgba(119, 227, 246, 0.72)",
  };
}

function particleTarget(width: number, height: number, coarsePointer: boolean): number {
  const area = width * height;
  if (coarsePointer || width < 760) {
    return clamp(Math.round(area / 42000), MOBILE_MIN_PARTICLES, MOBILE_MAX_PARTICLES);
  }
  return clamp(Math.round(area / 34000), DESKTOP_MIN_PARTICLES, DESKTOP_MAX_PARTICLES);
}

function createParticle(width: number, height: number, edge = false): Particle {
  const angle = Math.random() * Math.PI * 2;
  const speed = 0.18 + Math.random() * 0.42;
  return {
    x: edge ? Math.random() * width : Math.random() * width,
    y: edge ? height + 18 : Math.random() * height,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed,
    drift: 0.5 + Math.random() * 1.6,
    opacity: 0.52 + Math.random() * 0.44,
    radius: 1.55 + Math.random() * 2.85,
    life: 80 + Math.random() * 220,
    maxLife: 260 + Math.random() * 260,
    tone: Math.floor(Math.random() * 4),
  };
}

function createTrailParticle(x: number, y: number): Particle {
  const angle = Math.random() * Math.PI * 2;
  return {
    x,
    y,
    vx: Math.cos(angle) * 0.32,
    vy: Math.sin(angle) * 0.32,
    drift: 1.8,
    opacity: 0.86,
    radius: 2.2 + Math.random() * 3.1,
    life: 0,
    maxLife: 70 + Math.random() * 30,
    tone: 0,
  };
}

function flowVector(x: number, y: number, time: number, width: number, height: number) {
  const nx = x / Math.max(width, 1) - 0.5;
  const ny = y / Math.max(height, 1) - 0.5;
  const swirl = Math.sin((nx * 3.2 + time * 0.00017) * Math.PI) * 0.55;
  const wave = Math.cos((ny * 3.8 - time * 0.00014) * Math.PI) * 0.5;
  const orbitX = -ny * 0.74;
  const orbitY = nx * 0.74;

  return {
    x: orbitX + Math.cos(swirl + time * 0.00038) * 0.42,
    y: orbitY + Math.sin(wave + time * 0.00032) * 0.42,
  };
}

function isStaticBackdrop(width: number, coarsePointer: boolean): boolean {
  return coarsePointer || width < 760;
}

function setCanvasSize(
  canvas: HTMLCanvasElement,
  width: number,
  height: number,
  coarsePointer: boolean,
): number {
  const maxDpr = isStaticBackdrop(width, coarsePointer) ? 1 : 1.5;
  const dpr = Math.min(window.devicePixelRatio || 1, maxDpr);
  canvas.width = Math.max(1, Math.floor(width * dpr));
  canvas.height = Math.max(1, Math.floor(height * dpr));
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  return dpr;
}

export function SimulationBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvasElement = canvasRef.current;
    if (!canvasElement) {
      return undefined;
    }
    const renderingContext = canvasElement.getContext("2d");
    if (!renderingContext) {
      return undefined;
    }
    const canvas = canvasElement;
    const context = renderingContext;

    const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const coarsePointerQuery = window.matchMedia("(pointer: coarse)");
    const particles: Particle[] = [];
    const trails: Particle[] = [];
    const pointer: PointerState = {
      active: false,
      x: 0,
      y: 0,
      lastX: 0,
      lastY: 0,
      lastTrailAt: 0,
    };

    let width = window.innerWidth;
    let height = window.innerHeight;
    let dpr = setCanvasSize(canvas, width, height, coarsePointerQuery.matches);
    let animationFrame: number | null = null;
    let idleHandle: number | null = null;
    let idleTimeout: ReturnType<typeof globalThis.setTimeout> | null = null;
    let resizeTimeout: number | null = null;
    let running = false;
    let initialized = false;
    let lastFrameTime = 0;

    function seedParticles() {
      const target = particleTarget(width, height, coarsePointerQuery.matches);
      while (particles.length < target) {
        particles.push(createParticle(width, height));
      }
      particles.splice(target);
    }

    function drawParticle(particle: Particle, palette: Palette, isTrail = false) {
      const fadeIn = clamp(particle.life / 42, 0, 1);
      const fadeOut = clamp((particle.maxLife - particle.life) / 90, 0, 1);
      const alpha = particle.opacity * Math.min(fadeIn, fadeOut);
      const color = isTrail ? palette.trail : palette.particle[particle.tone % palette.particle.length];
      context.beginPath();
      context.fillStyle = color.replace(/[\d.]+\)$/u, `${alpha})`);
      context.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      context.fill();
    }

    function drawConnections(palette: Palette) {
      const isMobile = coarsePointerQuery.matches || width < 760;
      const distance = isMobile ? 74 : 112;
      const maxGap = distance * distance;
      const maxConnections = isMobile ? MAX_CONNECTIONS_MOBILE : MAX_CONNECTIONS_DESKTOP;
      const step = isMobile ? 3 : 2;
      let drawn = 0;

      for (let i = 0; i < particles.length; i += step) {
        for (let j = i + step; j < particles.length; j += step) {
          const first = particles[i];
          const second = particles[j];
          const dx = first.x - second.x;
          const dy = first.y - second.y;
          const gap = dx * dx + dy * dy;
          if (gap > maxGap) {
            continue;
          }
          const alpha = (1 - Math.sqrt(gap) / distance) * (isMobile ? 0.12 : 0.2);
          context.beginPath();
          context.strokeStyle = palette.connection.replace(/[\d.]+\)$/u, `${alpha})`);
          context.lineWidth = 0.75;
          context.moveTo(first.x, first.y);
          context.lineTo(second.x, second.y);
          context.stroke();
          drawn += 1;
          if (drawn >= maxConnections) {
            return;
          }
        }
      }
    }

    function drawFrame(time: number) {
      const palette = getPalette();
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, width, height);
      context.fillStyle = palette.background;
      context.fillRect(0, 0, width, height);

      drawConnections(palette);

      for (let index = particles.length - 1; index >= 0; index -= 1) {
        const particle = particles[index];
        const flow = flowVector(particle.x, particle.y, time, width, height);
        particle.vx = particle.vx * 0.968 + flow.x * 0.035 * particle.drift;
        particle.vy = particle.vy * 0.968 + flow.y * 0.035 * particle.drift;

        if (pointer.active && !reducedMotionQuery.matches && !coarsePointerQuery.matches) {
          const dx = pointer.x - particle.x;
          const dy = pointer.y - particle.y;
          const distance = Math.hypot(dx, dy);
          const radius = 180;
          if (distance > 0 && distance < radius) {
            const force = (1 - distance / radius) * 0.12;
            particle.vx -= (dy / distance) * force;
            particle.vy += (dx / distance) * force;
            particle.vx += (dx / distance) * force * 0.3;
            particle.vy += (dy / distance) * force * 0.3;
          }
        }

        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life += 1;

        if (
          particle.life > particle.maxLife ||
          particle.x < -32 ||
          particle.x > width + 32 ||
          particle.y < -32 ||
          particle.y > height + 32
        ) {
          particles[index] = createParticle(width, height, true);
        }

        drawParticle(particle, palette);
      }

      for (let index = trails.length - 1; index >= 0; index -= 1) {
        const trail = trails[index];
        const flow = flowVector(trail.x, trail.y, time, width, height);
        trail.vx += flow.x * 0.015;
        trail.vy += flow.y * 0.015;
        trail.x += trail.vx;
        trail.y += trail.vy;
        trail.life += 1;
        trail.opacity *= 0.975;
        if (trail.life > trail.maxLife) {
          trails.splice(index, 1);
        } else {
          drawParticle(trail, palette, true);
        }
      }
    }

    function tick(time: number) {
      if (!running) {
        return;
      }
      if (time - lastFrameTime >= FRAME_INTERVAL_MS) {
        lastFrameTime = time;
        drawFrame(time);
      }
      animationFrame = window.requestAnimationFrame(tick);
    }

    function start() {
      if (
        running ||
        reducedMotionQuery.matches ||
        isStaticBackdrop(width, coarsePointerQuery.matches) ||
        document.hidden
      ) {
        return;
      }
      running = true;
      animationFrame = window.requestAnimationFrame(tick);
    }

    function stop() {
      running = false;
      if (animationFrame !== null) {
        window.cancelAnimationFrame(animationFrame);
        animationFrame = null;
      }
      lastFrameTime = 0;
    }

    function drawStaticSnapshot() {
      const palette = getPalette();
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, width, height);
      context.fillStyle = palette.background;
      context.fillRect(0, 0, width, height);
      particles.forEach((particle) => drawParticle(particle, palette));
    }

    function resizeCanvas() {
      width = window.innerWidth;
      height = window.innerHeight;
      dpr = setCanvasSize(canvas, width, height, coarsePointerQuery.matches);
      seedParticles();
      if (reducedMotionQuery.matches || isStaticBackdrop(width, coarsePointerQuery.matches)) {
        stop();
        drawStaticSnapshot();
      } else {
        start();
      }
    }

    function onResize() {
      if (resizeTimeout !== null) {
        window.clearTimeout(resizeTimeout);
      }
      resizeTimeout = window.setTimeout(() => {
        resizeTimeout = null;
        resizeCanvas();
      }, RESIZE_DEBOUNCE_MS);
    }

    function onVisibilityChange() {
      if (document.hidden) {
        stop();
      } else {
        start();
      }
    }

    function onMotionPreferenceChange() {
      if (reducedMotionQuery.matches) {
        stop();
        pointer.active = false;
        drawStaticSnapshot();
      } else {
        if (isStaticBackdrop(width, coarsePointerQuery.matches)) {
          drawStaticSnapshot();
          return;
        }
        start();
      }
    }

    function onPointerMove(event: PointerEvent) {
      pointer.active = true;
      pointer.lastX = pointer.x || event.clientX;
      pointer.lastY = pointer.y || event.clientY;
      pointer.x = event.clientX;
      pointer.y = event.clientY;

      const now = window.performance.now();
      const moved = Math.hypot(pointer.x - pointer.lastX, pointer.y - pointer.lastY);
      if (moved > 5 && now - pointer.lastTrailAt > 72 && trails.length < 18) {
        pointer.lastTrailAt = now;
        trails.push(createTrailParticle(pointer.x, pointer.y));
      }
    }

    function onPointerLeave() {
      pointer.active = false;
    }

    function initialize() {
      initialized = true;
      seedParticles();
      if (reducedMotionQuery.matches || isStaticBackdrop(width, coarsePointerQuery.matches)) {
        drawStaticSnapshot();
      } else {
        start();
      }
    }

    if ("requestIdleCallback" in window) {
      idleHandle = window.requestIdleCallback(initialize, { timeout: 700 });
    } else {
      idleTimeout = globalThis.setTimeout(initialize, 240);
    }

    window.addEventListener("resize", onResize, { passive: true });
    document.addEventListener("visibilitychange", onVisibilityChange);
    reducedMotionQuery.addEventListener("change", onMotionPreferenceChange);

    if (!reducedMotionQuery.matches && !coarsePointerQuery.matches) {
      window.addEventListener("pointermove", onPointerMove, { passive: true });
      window.addEventListener("pointerleave", onPointerLeave, { passive: true });
    }

    return () => {
      stop();
      if (idleHandle !== null) {
        if ("cancelIdleCallback" in window && initialized === false) {
          window.cancelIdleCallback(idleHandle);
        }
      }
      if (idleTimeout !== null) {
        globalThis.clearTimeout(idleTimeout);
      }
      if (resizeTimeout !== null) {
        window.clearTimeout(resizeTimeout);
      }
      window.removeEventListener("resize", onResize);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      reducedMotionQuery.removeEventListener("change", onMotionPreferenceChange);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerleave", onPointerLeave);
    };
  }, []);

  return (
    <div aria-hidden="true" className="simulation-backdrop" data-testid="simulation-backdrop">
      <canvas
        aria-hidden="true"
        className="simulation-canvas"
        data-testid="simulation-canvas"
        ref={canvasRef}
        style={{ pointerEvents: "none" }}
      />
      <div className="simulation-grid" />
      <div className="simulation-orbit simulation-orbit-one" />
      <div className="simulation-orbit simulation-orbit-two" />
      <div className="simulation-core" />
      <div className="simulation-scan" />
    </div>
  );
}
