"use client";

import { useEffect, useState } from "react";

const TICK = 1000;

export const useCountdown = (deadline: number) => {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), TICK);

    return () => window.clearInterval(timer);
  }, []);

  const left = Math.max(0, Math.ceil((deadline - now) / TICK));

  return left;
};
