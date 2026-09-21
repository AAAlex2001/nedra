import { ArticlesSlider, type ArticleCardData } from "@/entities/article";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

type ArticlesProps = {
  items: ArticleCardData[];
};

const Articles = ({ items }: ArticlesProps) => (
  <section className={styles.articles}>
    <div className={styles.heading}>
      <h2 className={styles.title}>Разбираем экспертизу по шагам</h2>
      <p className={styles.lead}>
        Сроки, штрафы, документы и требования Ростехнадзора — без канцелярита,
        со ссылками на первоисточники.
      </p>
    </div>

    <ArticlesSlider articles={items} ariaLabel="Статьи об экспертизе промышленной безопасности" />

    <Button className={styles.more} href="/novosti">
      Все материалы
    </Button>
  </section>
);

export default Articles;
