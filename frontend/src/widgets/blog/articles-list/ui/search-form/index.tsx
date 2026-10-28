"use client";

import { useEffect, useState, type FormEvent } from "react";
import { NedraMarkIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type SearchFormProps = {
  initialValue: string;
  pending: boolean;
  onSearch: (value: string) => void;
};

const MIN_LENGTH = 2;
const DEBOUNCE_MS = 400;

const isSearchable = (search: string): boolean => search === "" || search.length >= MIN_LENGTH;

const SearchForm = ({ initialValue, pending, onSearch }: SearchFormProps) => {
  const [value, setValue] = useState(initialValue);

  const search = value.trim();

  useEffect(() => {
    if (pending || search === initialValue || !isSearchable(search)) return;

    const timer = window.setTimeout(() => onSearch(search), DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }, [search, initialValue, pending, onSearch]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSearch(search);
  };

  return (
    <form className={styles.form} role="search" onSubmit={handleSubmit}>
      <NedraMarkIcon className={styles.mark} />

      <input
        className={styles.input}
        type="search"
        name="q"
        placeholder="Поиск по заголовку"
        aria-label="Поиск по заголовку"
        autoComplete="off"
        maxLength={100}
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />

      <button type="submit" className={styles.submit} disabled={pending}>
        Найти
      </button>
    </form>
  );
};

export default SearchForm;
