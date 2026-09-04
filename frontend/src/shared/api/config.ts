/**
 * Адрес API для браузера. Значение вшивается в бандл на этапе сборки
 * (build arg NEXT_PUBLIC_API_URL), поэтому смена требует пересборки.
 * Дефолт рассчитан на nginx, который проксирует /api на backend.
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";
