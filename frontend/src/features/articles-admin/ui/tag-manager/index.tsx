"use client";

import type { TagAdmin } from "@/entities/article";
import Button from "@/shared/ui/button";
import { useTags } from "../../model/use-tags";
import styles from "./style.module.scss";

type TagManagerProps = {
  basePath: string;
  initialItems: TagAdmin[];
};

const TagManager = ({ basePath, initialItems }: TagManagerProps) => {
  const { state, changeDraft, add, remove } = useTags(basePath, initialItems);

  return (
    <section className={styles.root}>
      <h2 className={styles.title}>Теги</h2>

      <form
        className={styles.form}
        onSubmit={(event) => {
          event.preventDefault();
          void add();
        }}
      >
        <input
          className={styles.input}
          placeholder="Новый тег, например «Промышленная безопасность»"
          maxLength={100}
          value={state.draft}
          onChange={(event) => changeDraft(event.target.value)}
        />
        <Button type="submit" disabled={state.pending || state.draft.trim().length < 2}>
          Добавить
        </Button>
      </form>

      {state.error && <p className={styles.error}>{state.error}</p>}

      {state.items.length === 0 ? (
        <p className={styles.empty}>Тегов пока нет.</p>
      ) : (
        <ul className={styles.list}>
          {state.items.map((tag) => (
            <li key={tag.id} className={styles.chip}>
              {tag.title}
              <button
                type="button"
                className={styles.remove}
                aria-label={`Удалить тег ${tag.title}`}
                disabled={state.pending}
                onClick={() => {
                  if (window.confirm(`Удалить тег «${tag.title}»? Он снимется со всех статей.`)) {
                    void remove(tag.id);
                  }
                }}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};

export default TagManager;
