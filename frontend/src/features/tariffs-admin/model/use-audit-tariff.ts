"use client";

import { useState } from "react";
import { AUDIT_TARIFF, isAuditTariff, type Tariff } from "@/entities/tariff";
import { keepDigits } from "@/shared/lib/text";
import { saveTariffs } from "../api/tariffs";

type SaveStatus = "idle" | "saving" | "saved";

const priceOf = (tariffs: Tariff[]): string => {
  const tariff = tariffs.find(isAuditTariff);

  return tariff ? String(Math.round(Number(tariff.price))) : "";
};

export const useAuditTariff = (initialTariffs: Tariff[], basePath: string) => {
  const [saved, setSaved] = useState(priceOf(initialTariffs));
  const [price, setPrice] = useState(saved);
  const [status, setStatus] = useState<SaveStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const dirty = price !== saved;

  const change = (value: string) => {
    setPrice(keepDigits(value));
    setStatus("idle");
  };

  const save = async () => {
    setStatus("saving");
    setError(null);

    try {
      const tariffs = await saveTariffs(basePath, [
        { ...AUDIT_TARIFF, price: price === "" ? null : price },
      ]);
      const fresh = priceOf(tariffs);
      setSaved(fresh);
      setPrice(fresh);
      setStatus("saved");
    } catch (caught) {
      setError(caught instanceof Error && caught.message ? caught.message : "Не удалось сохранить тариф");
      setStatus("idle");
    }
  };

  return { price, dirty, status, error, change, save };
};
