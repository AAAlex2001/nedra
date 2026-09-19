import type { ExpertCatalog } from "../model/types";

export const directionTitle = (catalog: ExpertCatalog, code: string): string => {
  const direction = catalog.directions.find((item) => item.code === code);

  return direction ? direction.title : code;
};

export const objectLabel = (catalog: ExpertCatalog, code: string): string => {
  const object = catalog.objects.find((item) => item.code === code);

  return object ? object.label : code;
};

export const objectTitle = (catalog: ExpertCatalog, code: string): string => {
  const object = catalog.objects.find((item) => item.code === code);

  return object ? object.title : code;
};

export const areaTitle = (catalog: ExpertCatalog, code: string): string => {
  const area = catalog.areas.find((item) => item.code === code);

  return area ? area.title : code;
};

export const formatCategory = (category: number): string => `${category} кат.`;
