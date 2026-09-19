export type SaveStatus = "idle" | "saving" | "saved" | "error";

export type TariffGridState = {
  values: Record<string, string>;
  dirty: boolean;
  status: SaveStatus;
  error: string | null;
};

export type TariffGridAction =
  | { type: "cell/change"; key: string; value: string }
  | { type: "save/start" }
  | { type: "save/success"; values: Record<string, string> }
  | { type: "save/error"; message: string };
