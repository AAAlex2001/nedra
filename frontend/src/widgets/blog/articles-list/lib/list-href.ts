type ListQuery = {
  tag: string | null;
  search: string;
  page?: number;
};

export const buildListHref = (basePath: string, { tag, search, page }: ListQuery): string => {
  const params = new URLSearchParams();

  if (tag) params.set("tag", tag);
  if (search) params.set("q", search);
  if (page && page > 1) params.set("page", String(page));

  const query = params.toString();

  return query ? `${basePath}?${query}` : basePath;
};
