"use client";

import { useEffect, useState } from "react";

const TICK = 1000;

export const useCountdown = () => {
  const [deadline, setDeadline] = useState(0);
  const [now, setNow] = useState(0);

  const left = Math.max(0, Math.ceil((deadline - now) / TICK));
  const running = left > 0;

  useEffect(() => {
    if (!running) return;

    const timer = window.setInterval(() => setNow(Date.now()), TICK);

    return () => window.clearInterval(timer);
  }, [running]);

  const start = (seconds: number) => {
    const current = Date.now();

    setNow(current);
    setDeadline(current + seconds * TICK);
  };

  return { left, running, start };
};
