"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import SearchForm from "@/shared/ui/search-form";
import { buildAdminListHref, type AdminListFilters } from "../../lib/list-href";

type ArticlesSearchProps = {
  listPath: string;
  filters: AdminListFilters;
};

const ArticlesSearch = ({ listPath, filters }: ArticlesSearchProps) => {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  const runSearch = (search: string) => {
    const href = buildAdminListHref(listPath, {
      section: filters.section,
      sort: filters.sort,
      search,
    });

    startTransition(() => router.replace(href, { scroll: false }));
  };

  return (
    <SearchForm
      initialValue={filters.search}
      pending={pending}
      onSearch={runSearch}
      placeholder="Поиск по заголовку статьи"
    />
  );
};

export default ArticlesSearch;
