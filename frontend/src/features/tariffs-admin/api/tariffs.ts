import type { Tariff } from "@/entities/tariff";
import { readErrorMessage } from "@/shared/api";

export type TariffChange = {
  area_code: string;
  object_code: string;
  price: string | null;
};

export const saveTariffs = async (
  basePath: string,
  items: TariffChange[],
): Promise<Tariff[]> => {
  const response = await fetch(`${basePath}/api/tariffs`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const tariffs: Tariff[] = await response.json();

  return tariffs;
};
