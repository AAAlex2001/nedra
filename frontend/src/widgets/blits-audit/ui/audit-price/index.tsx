"use client";

import classNames from "classnames";
import { useStartAction } from "@/features/auth";
import { formatRub, halfOf } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import { CheckIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type AuditPriceProps = {
  price: string | null;
  startText: string;
};

const NOTES = [
  {
    text: "Аудитор проверяет документы по перечню из 47 пунктов. Загрузить можно не всё — недостающее он отметит в отчёте.",
    bold: false,
  },
  {
    text: "По каждому несоответствию — что исправить до проверки Ростехнадзора. Отчёт подписан ЭЦП.",
    bold: false,
  },
  {
    text: "Это цена по тарифу института. В заявке вы можете указать свою — аудитор возьмёт её, если согласен.",
    bold: true,
  },
];

const AuditPrice = ({ price, startText }: AuditPriceProps) => {
  const start = useStartAction();
  const advance = halfOf(price);

  return (
    <section className={styles.price} id="stoimost">
      <div className={styles.heading}>
        <h2 className={styles.title}>Стоимость аудита — до регистрации</h2>
        <p className={styles.lead}>
          Действующий тариф института на аудит СУПБ. Свою цену вы предложите в заявке, она
          войдёт в договор.
        </p>
      </div>

      <div className={styles.body}>
        <ul className={styles.notes}>
          {NOTES.map((note) => (
            <li key={note.text} className={styles.note}>
              <CheckIcon className={styles.noteIcon} />
              <span className={classNames(styles.noteText, note.bold && styles.noteBold)}>
                {note.text}
              </span>
            </li>
          ))}
        </ul>

        <aside className={styles.result}>
          <span className={styles.resultLabel}>Стоимость аудита СУПБ</span>
          <span className={styles.resultPrice}>{formatRub(price)}</span>
          <span className={styles.resultSplit}>
            {advance
              ? `Аванс ${formatRub(advance)}, столько же после готовности отчёта`
              : "Оплата двумя частями: аванс и остаток после готовности отчёта"}
          </span>

          <dl className={styles.facts}>
            <div className={styles.fact}>
              <dt className={styles.factLabel}>Формат</dt>
              <dd className={styles.factValue}>по документам</dd>
            </div>
            <div className={styles.fact}>
              <dt className={styles.factLabel}>Документ</dt>
              <dd className={styles.factValue}>отчёт с ЭЦП</dd>
            </div>
          </dl>

          <Button className={styles.submit} onClick={start}>
            {startText}
          </Button>
        </aside>
      </div>
    </section>
  );
};

export default AuditPrice;
