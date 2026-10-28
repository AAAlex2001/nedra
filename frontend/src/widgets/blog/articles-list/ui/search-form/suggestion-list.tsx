import classNames from "classnames";
import Link from "next/link";
import { articlePath, type ArticleSuggestion } from "@/entities/article";
import styles from "./style.module.scss";

type SuggestionListProps = {
  id: string;
  items: ArticleSuggestion[];
  search: string;
  activeIndex: number;
  onPick: () => void;
};

export const optionId = (listId: string, index: number) => `${listId}-${index}`;

const HighlightedTitle = ({ title, search }: { title: string; search: string }) => {
  const start = title.toLowerCase().indexOf(search.trim().toLowerCase());

  if (start < 0) return <>{title}</>;

  const end = start + search.trim().length;

  return (
    <>
      {title.slice(0, start)}
      <mark className={styles.match}>{title.slice(start, end)}</mark>
      {title.slice(end)}
    </>
  );
};

const SuggestionList = ({ id, items, search, activeIndex, onPick }: SuggestionListProps) => (
  <ul id={id} className={styles.list} role="listbox" aria-label="Подсказки">
    {items.map((item, index) => (
      <li key={item.slug} id={optionId(id, index)} role="option" aria-selected={index === activeIndex}>
        <Link
          href={articlePath(item)}
          className={classNames(styles.option, index === activeIndex && styles.optionActive)}
          tabIndex={-1}
          onClick={onPick}
        >
          <HighlightedTitle title={item.title} search={search} />
        </Link>
      </li>
    ))}
  </ul>
);

export default SuggestionList;
