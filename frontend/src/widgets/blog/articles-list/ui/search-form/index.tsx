"use client";

import { useState, type FormEvent } from "react";
import { NedraMarkIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type SearchFormProps = {
  initialValue: string;
  pending: boolean;
  onSearch: (value: string) => void;
};

const SearchForm = ({ initialValue, pending, onSearch }: SearchFormProps) => {
  const [value, setValue] = useState(initialValue);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSearch(value.trim());
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
