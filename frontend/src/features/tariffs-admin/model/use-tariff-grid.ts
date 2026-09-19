"use client";

import { useReducer } from "react";
import { tariffKey, type Tariff } from "@/entities/tariff";
import { keepDigits } from "@/shared/lib/text";
import { saveTariffs, type TariffChange } from "../api/tariffs";
import { tariffGridReducer } from "./reducer";

const toValues = (tariffs: Tariff[]): Record<string, string> => {
  const values: Record<string, string> = {};

  for (const tariff of tariffs) {
    const key = tariffKey(tariff.area_code, tariff.object_code);
    values[key] = String(Math.round(Number(tariff.price)));
  }

  return values;
};

const toChanges = (values: Record<string, string>): TariffChange[] => {
  const changes: TariffChange[] = [];

  for (const key of Object.keys(values)) {
    const [areaCode, objectCode] = key.split(":");
    const price = values[key];

    changes.push({
      area_code: areaCode,
      object_code: objectCode,
      price: price === "" ? null : price,
    });
  }

  return changes;
};

export const useTariffGrid = (initialTariffs: Tariff[], basePath: string) => {
  const [state, dispatch] = useReducer(tariffGridReducer, {
    values: toValues(initialTariffs),
    dirty: false,
    status: "idle",
    error: null,
  });

  const changeCell = (key: string, value: string) =>
    dispatch({ type: "cell/change", key, value: keepDigits(value) });

  const save = async () => {
    dispatch({ type: "save/start" });

    try {
      const tariffs = await saveTariffs(basePath, toChanges(state.values));
      dispatch({ type: "save/success", values: toValues(tariffs) });
    } catch (error) {
      const message =
        error instanceof Error && error.message ? error.message : "Не удалось сохранить тарифы";
      dispatch({ type: "save/error", message });
    }
  };

  return { state, changeCell, save };
};
