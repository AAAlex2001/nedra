"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition, type FormEvent } from "react";
import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import { buildAdminListHref, type AdminListFilters } from "../../lib/list-href";
import styles from "./style.module.scss";

type ArticlesSearchProps = {
  listPath: string;
  filters: AdminListFilters;
};

const MIN_LENGTH = 2;
const DEBOUNCE_MS = 400;

const isSearchable = (search: string): boolean => search === "" || search.length >= MIN_LENGTH;

const ArticlesSearch = ({ listPath, filters }: ArticlesSearchProps) => {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [value, setValue] = useState(filters.search);

  const search = value.trim();

  const runSearch = (nextSearch: string) => {
    const href = buildAdminListHref(listPath, {
      section: filters.section,
      sort: filters.sort,
      search: nextSearch,
    });

    startTransition(() => router.replace(href, { scroll: false }));
  };

  useEffect(() => {
    if (pending || search === filters.search || !isSearchable(search)) return;

    const timer = window.setTimeout(() => runSearch(search), DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    runSearch(search);
  };

  return (
    <form className={styles.form} role="search" onSubmit={handleSubmit}>
      <div className={styles.field}>
        <TextField
          placeholder="Поиск по заголовку статьи"
          maxLength={100}
          value={value}
          onChange={setValue}
        />
      </div>
      <Button type="submit" className={styles.submit} loading={pending}>
        Найти
      </Button>
    </form>
  );
};

export default ArticlesSearch;
