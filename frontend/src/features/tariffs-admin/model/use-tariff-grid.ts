"use client";

import { useReducer } from "react";
import { tariffKey, type Tariff } from "@/entities/tariff";
import { keepDigits } from "@/shared/lib/text";
import { saveTariffs, type TariffChange } from "../api/tariffs";
import { tariffGridReducer } from "./reducer";

const toValues = (tariffs: Tariff[]): Record<string, string> => {
  const values: Record<string, string> = {};

  for (const tariff of tariffs) {
    values[tariffKey(tariff.area_code, tariff.object_code)] = String(Math.round(Number(tariff.price)));
  }

  return values;
};

export const useTariffGrid = (initialTariffs: Tariff[], basePath: string) => {
  const initialValues = toValues(initialTariffs);
  const [state, dispatch] = useReducer(tariffGridReducer, {
    values: initialValues,
    saved: initialValues,
    status: "idle",
    error: null,
  });

  const changedKeys = Object.keys({ ...state.saved, ...state.values }).filter(
    (key) => (state.saved[key] ?? "") !== (state.values[key] ?? ""),
  );

  const changeCell = (key: string, value: string) =>
    dispatch({ type: "cell/change", key, value: keepDigits(value) });

  const save = async () => {
    if (changedKeys.length === 0) return;

    dispatch({ type: "save/start" });

    const items: TariffChange[] = changedKeys.map((key) => {
      const [areaCode, objectCode] = key.split(":");
      const value = state.values[key] ?? "";

      return {
        area_code: areaCode,
        object_code: objectCode,
        price: value === "" ? null : value,
      };
    });

    try {
      const tariffs = await saveTariffs(basePath, items);
      dispatch({ type: "save/success", values: toValues(tariffs) });
    } catch (error) {
      const message =
        error instanceof Error && error.message ? error.message : "Не удалось сохранить тарифы";
      dispatch({ type: "save/error", message });
    }
  };

  return { state, changedKeys, changeCell, save };
};
