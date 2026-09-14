const OPTIMIZABLE_PREFIX = "/news/";

export const isOptimizableCover = (src: string): boolean => src.startsWith(OPTIMIZABLE_PREFIX);

export const CARD_COVER_SIZES = "(min-width: 1440px) 440px, (min-width: 768px) 50vw, 100vw";

export const ARTICLE_COVER_SIZES = "(min-width: 1440px) 900px, 100vw";
