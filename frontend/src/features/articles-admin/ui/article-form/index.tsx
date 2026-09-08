"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ArticleAdmin, TagAdmin } from "@/entities/article";
import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import { useArticleEditor } from "../../model/use-article-editor";
import styles from "./style.module.scss";

type ArticleFormProps = {
  basePath: string;
  article: ArticleAdmin | null;
  tags: TagAdmin[];
};

const ArticleForm = ({ basePath, article, tags }: ArticleFormProps) => {
  const router = useRouter();
  const { state, changeField, toggleTag, uploadCover, save } = useArticleEditor(
    basePath,
    article,
  );
  const { fields, status, uploading, error } = state;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const saved = await save();

    if (saved && !article) {
      router.push(`${basePath}/articles/${saved.id}`);
    }
  };

  return (
    <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
      <div className={styles.columns}>
        <div className={styles.main}>
          <TextField
            label="Заголовок"
            required
            maxLength={255}
            value={fields.title}
            onChange={(value) => changeField("title", value)}
          />

          <TextField
            label="Slug (адрес страницы)"
            placeholder="Оставьте пустым — соберётся из заголовка"
            maxLength={255}
            value={fields.slug}
            onChange={(value) => changeField("slug", value.toLowerCase())}
          />

          <TextField
            label="Краткое описание"
            multiline
            rows={3}
            maxLength={400}
            placeholder="Текст для карточки и сниппета в поиске, до 400 символов"
            value={fields.description}
            onChange={(value) => changeField("description", value)}
          />

          <label className={styles.field}>
            <span className={styles.label}>
              Текст статьи (HTML)<span className={styles.required}> *</span>
            </span>
            <textarea
              className={styles.code}
              rows={24}
              required
              placeholder="<h2>Заголовок раздела</h2>&#10;<p>Абзац текста…</p>"
              value={fields.content}
              onChange={(event) => changeField("content", event.target.value)}
            />
            <span className={styles.hint}>
              Оглавление собирается из тегов &lt;h2&gt;. Скрипты, стили и лишние атрибуты
              вырезаются при сохранении.
            </span>
          </label>
        </div>

        <aside className={styles.side}>
          <div className={styles.panel}>
            <span className={styles.label}>Обложка</span>

            <div className={styles.cover}>
              {fields.cover_image ? (
                <Image src={fields.cover_image} alt="" fill unoptimized className={styles.coverImage} />
              ) : (
                <span className={styles.coverEmpty}>Нет изображения</span>
              )}
            </div>

            <label className={styles.upload}>
              {uploading ? "Загружаем…" : "Загрузить файл"}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                disabled={uploading}
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) void uploadCover(file);
                  event.target.value = "";
                }}
              />
            </label>

            <TextField
              label="Или путь к картинке"
              placeholder="/media/articles/…"
              maxLength={500}
              value={fields.cover_image}
              onChange={(value) => changeField("cover_image", value)}
            />
          </div>

          <div className={styles.panel}>
            <span className={styles.label}>Теги</span>

            {tags.length === 0 ? (
              <span className={styles.hint}>Тегов ещё нет — добавьте их в списке статей.</span>
            ) : (
              <div className={styles.tags}>
                {tags.map((tag) => {
                  const checked = fields.tag_ids.includes(tag.id);

                  return (
                    <label
                      key={tag.id}
                      className={`${styles.tag} ${checked ? styles.tagActive : ""}`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleTag(tag.id)}
                      />
                      {tag.title}
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          <div className={styles.panel}>
            <span className={styles.label}>SEO</span>

            <TextField
              label="Title для поисковика"
              placeholder="Пусто — берётся заголовок статьи"
              maxLength={255}
              value={fields.seo_title}
              onChange={(value) => changeField("seo_title", value)}
            />

            <TextField
              label="Meta description"
              multiline
              rows={3}
              maxLength={300}
              placeholder="Пусто — берётся краткое описание. Оптимально 120–160 символов"
              value={fields.seo_description}
              onChange={(value) => changeField("seo_description", value)}
            />

            <TextField
              label="Ключевые слова"
              placeholder="через запятую"
              maxLength={500}
              value={fields.seo_keywords}
              onChange={(value) => changeField("seo_keywords", value)}
            />
          </div>

          <div className={styles.panel}>
            <label className={styles.checkbox}>
              <input
                type="checkbox"
                checked={fields.published}
                onChange={(event) => changeField("published", event.target.checked)}
              />
              Опубликована на сайте
            </label>

            {article?.published_at && (
              <Link
                href={`/blog/${article.slug}`}
                target="_blank"
                className={styles.link}
              >
                Открыть на сайте ↗
              </Link>
            )}
          </div>
        </aside>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.actions}>
        <Button type="submit" disabled={status === "saving" || uploading}>
          {status === "saving" ? "Сохраняем…" : article ? "Сохранить" : "Создать статью"}
        </Button>

        {status === "saved" && <span className={styles.saved}>Сохранено</span>}

        <Link href={`${basePath}/articles`} className={styles.back}>
          К списку статей
        </Link>
      </div>
    </form>
  );
};

export default ArticleForm;
