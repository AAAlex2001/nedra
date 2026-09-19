export type Tariff = {
  area_code: string;
  object_code: string;
  price: string;
  updated_at: string;
};

export const tariffKey = (areaCode: string, objectCode: string): string =>
  `${areaCode}:${objectCode}`;
