const HEADING = /<h2[^>]*>/g;

export const splitAtHeadings = (content: string, positions: number[]): string[] => {
  const starts = Array.from(content.matchAll(HEADING)).map((match) => match.index ?? 0);

  const cuts = positions
    .map((position) => starts[position - 1])
    .filter((index): index is number => index !== undefined && index > 0);

  const parts: string[] = [];
  let from = 0;

  for (const cut of cuts) {
    parts.push(content.slice(from, cut));
    from = cut;
  }

  parts.push(content.slice(from));

  return parts;
};
