"use client";

import { useEffect, useState } from "react";

const TICK = 1000;

export const useCountdown = (deadline: number) => {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    setNow(Date.now());

    const timer = window.setInterval(() => setNow(Date.now()), TICK);

    return () => window.clearInterval(timer);
  }, [deadline]);

  const left = Math.max(0, Math.ceil((deadline - now) / TICK));

  return left;
};
