export type Tariff = {
  area_code: string;
  object_code: string;
  price: string;
  updated_at: string;
};

export const tariffKey = (areaCode: string, objectCode: string): string =>
  `${areaCode}:${objectCode}`;

export const AUDIT_TARIFF = { area_code: "audit", object_code: "supb" };

export const isAuditTariff = (tariff: Tariff): boolean =>
  tariff.area_code === AUDIT_TARIFF.area_code && tariff.object_code === AUDIT_TARIFF.object_code;
