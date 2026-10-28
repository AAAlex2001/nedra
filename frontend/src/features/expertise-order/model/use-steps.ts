"use client";

import { useState } from "react";
import type { FormErrors } from "./types";

export type OrderStep = {
  key: string;
  title: string;
  errors: FormErrors;
};

const hasErrors = (step: OrderStep): boolean => Object.keys(step.errors).length > 0;

export const useSteps = (list: OrderStep[]) => {
  const [index, setIndex] = useState(0);
  const [attempted, setAttempted] = useState(false);

  const current = list[index];
  const upcoming = list[index + 1] ?? null;
  const isFirst = index === 0;
  const isLast = index === list.length - 1;
  const errors = attempted ? current.errors : {};

  const goTo = (target: number) => {
    setAttempted(false);
    setIndex(target);
  };

  const validate = (): boolean => {
    setAttempted(true);
    return !hasErrors(current);
  };

  const next = () => {
    if (validate()) goTo(index + 1);
  };

  const back = () => goTo(index - 1);
  const reset = () => goTo(0);

  return { list, index, current, upcoming, isFirst, isLast, errors, validate, next, back, reset };
};

export type Steps = ReturnType<typeof useSteps>;
