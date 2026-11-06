import { DIRECTIONS } from "@/entities/service";
import Link from "next/link";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import Faq from "@/shared/ui/faq";
import TableOfContents from "@/shared/ui/table-of-contents";
import RequestWidget from "@/widgets/blog/article-page/ui/request-widget";
import StickyAside from "@/widgets/blog/article-page/ui/sticky-aside";
import articleStyles from "@/widgets/blog/article-page/style.module.scss";
import DirectionSection from "./ui/direction-section";
import ServicesHero from "./ui/hero";
import { SERVICES_FAQ } from "./data";
import styles from "./style.module.scss";

const contents = [
  ...DIRECTIONS.map(direction => ({
    id: `direction-${direction.id}`,
    title: direction.title,
  })),
  {
    id: "service-order",
    title: "Как заказать работы",
  },
];

const Services = () => (
  <main className={styles.page}>
    <Breadcrumbs
      items={[
        { label: "Главная", href: "/" },
        { label: "Услуги" },
      ]}
    />
    <div className={styles.inner}>
      <ServicesHero />

      <div className={articleStyles.layout}>
        <div className={styles.directions} data-toc-content>
          <TableOfContents items={contents} />
          {DIRECTIONS.map(direction => (
            <DirectionSection key={direction.id} direction={direction} />
          ))}

          <section className={styles.orderGuide} aria-labelledby="service-order">
            <h2 id="service-order">Как определить состав работ, стоимость и сроки</h2>
            <ol>
              <li>
                <h3>Опишите задачу и объект</h3>
                <p>
                  Что планируется: строительство, реконструкция, эксплуатация,
                  обследование, испытания или обучение? Укажите текущую стадию,
                  имеющиеся замечания и нужный результат.
                </p>
              </li>
              <li>
                <h3>Подготовьте имеющиеся материалы</h3>
                <p>
                  Проект, технические паспорта, результаты исследований или текст
                  замечаний помогут оценить объём задачи. Если часть документов
                  отсутствует, сообщите об этом при обращении.
                </p>
              </li>
              <li>
                <h3>Согласуйте условия до начала работ</h3>
                <p>
                  Уточните состав работ, перечень выдаваемых документов, необходимые
                  исходные данные, стоимость и сроки. Для задач с несколькими этапами
                  важно согласовать их последовательность.
                </p>
              </li>
            </ol>
            <p>
              Для подачи документов через личный кабинет доступны{' '}
              <Link href="/blits-ekspert">Блиц-эксперт — экспертиза промышленной безопасности</Link>
              {' '}и{' '}
              <Link href="/blits-audit">Блиц-аудит — аудит СУПБ</Link>.
              {' '}Если направление пока не определено,{' '}
              <a href="#request">оставьте заявку с описанием задачи</a>.
            </p>
          </section>

          <Faq
            className={styles.faq}
            title="Стоимость, сроки и подготовка к заказу: вопросы и ответы"
            items={SERVICES_FAQ}
          />
        </div>

        <StickyAside className={articleStyles.widget}>
          <RequestWidget />
        </StickyAside>
      </div>
    </div>
  </main>
);

export default Services;
