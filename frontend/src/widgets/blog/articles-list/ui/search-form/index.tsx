"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { articlePath, type ArticleSection, type ArticleSuggestion } from "@/entities/article";
import { NedraMarkIcon } from "@/shared/ui/icons";
import { useSuggestions } from "../../model/use-suggestions";
import SuggestionList, { optionId } from "./suggestion-list";
import styles from "./style.module.scss";

type SearchFormProps = {
  section: ArticleSection;
  initialValue: string;
  pending: boolean;
  onSearch: (value: string) => void;
};

const SearchForm = ({ section, initialValue, pending, onSearch }: SearchFormProps) => {
  const router = useRouter();
  const listId = useId();
  const rootRef = useRef<HTMLFormElement>(null);

  const [value, setValue] = useState(initialValue);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const suggestions = useSuggestions(section, value);
  const showList = open && suggestions.length > 0;
  const activeSuggestion = showList ? suggestions[activeIndex] : undefined;

  useEffect(() => {
    if (!open) return;

    const closeOnClickOutside = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };

    document.addEventListener("mousedown", closeOnClickOutside);

    return () => document.removeEventListener("mousedown", closeOnClickOutside);
  }, [open]);

  const closeList = () => {
    setOpen(false);
    setActiveIndex(-1);
  };

  const changeValue = (next: string) => {
    setValue(next);
    setActiveIndex(-1);
    setOpen(true);
  };

  const moveActive = (step: number) => {
    const count = suggestions.length;

    if (activeIndex < 0) {
      setActiveIndex(step > 0 ? 0 : count - 1);
      return;
    }

    setActiveIndex((activeIndex + step + count) % count);
  };

  const openArticle = (item: ArticleSuggestion) => {
    closeList();
    router.push(articlePath(item));
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (!showList) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveActive(1);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveActive(-1);
      return;
    }

    if (event.key === "Escape") {
      closeList();
      return;
    }

    if (event.key === "Enter" && activeSuggestion) {
      event.preventDefault();
      openArticle(activeSuggestion);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    closeList();
    onSearch(value.trim());
  };

  return (
    <form ref={rootRef} className={styles.form} role="search" onSubmit={handleSubmit}>
      <NedraMarkIcon className={styles.mark} />

      <input
        className={styles.input}
        type="search"
        name="q"
        role="combobox"
        placeholder="Поиск по заголовку"
        aria-label="Поиск по заголовку"
        aria-autocomplete="list"
        aria-expanded={showList}
        aria-controls={listId}
        aria-activedescendant={activeSuggestion ? optionId(listId, activeIndex) : undefined}
        autoComplete="off"
        maxLength={100}
        value={value}
        onChange={(event) => changeValue(event.target.value)}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
      />

      <button type="submit" className={styles.submit} disabled={pending}>
        Найти
      </button>

      {showList && (
        <SuggestionList
          id={listId}
          items={suggestions}
          search={value}
          activeIndex={activeIndex}
          onPick={closeList}
        />
      )}
    </form>
  );
};

export default SearchForm;
