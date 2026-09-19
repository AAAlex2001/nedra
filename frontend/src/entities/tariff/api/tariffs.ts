import { API_URL, readErrorMessage } from "@/shared/api";
import type { Tariff } from "../model/types";

export const fetchTariffs = async (): Promise<Tariff[]> => {
  const response = await fetch(`${API_URL}/v1/tariffs`, { cache: "no-store" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const tariffs: Tariff[] = await response.json();

  return tariffs;
};
