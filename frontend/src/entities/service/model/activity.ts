import { DIRECTIONS } from "./catalog";

/**
 * Связь услуги каталога с числовым activity на бэкенде
 * (backend/app/services/requestDTO.py).
 *
 * Значения уже записаны в существующих заявках — менять их нельзя.
 * Новая услуга получает следующий свободный номер, и такой же номер
 * должен появиться в ACTIVITY_DIRECTION на бэкенде.
 */
export const ACTIVITY_BY_SERVICE_ID: Record<string, number> = {
  "01-1": 0,
  "02-1": 1,
  "02-2": 2,
  "02-3": 3,
  "03-1": 4,
  "03-2": 5,
  "03-3": 6,
  "03-4": 7,
  "03-5": 8,
  "03-6": 9,
  "03-7": 10,
  "04-1": 11,
  "05-1": 12,
  "06-1": 13,
  "07-1": 14,
  "08-1": 15,
  "09-1": 16,
};

export type ServiceOption = {
  id: string;
  label: string;
  activity: number;
};

export type DirectionOption = {
  id: string;
  title: string;
  image: string;
  serviceCount: number;
  services: ServiceOption[];
};

export const DIRECTION_OPTIONS: DirectionOption[] = DIRECTIONS.map(
  (direction) => ({
    id: direction.id,
    title: direction.title,
    image: direction.image,
    serviceCount: direction.serviceCount,
    services: direction.services.map((service) => ({
      id: service.id,
      label: service.label,
      activity: ACTIVITY_BY_SERVICE_ID[service.id],
    })),
  }),
);
