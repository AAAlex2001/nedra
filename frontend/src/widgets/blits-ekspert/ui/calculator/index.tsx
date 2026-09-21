"use client";

import { useState } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import { tariffKey, type Tariff } from "@/entities/tariff";
import { formatRub, halfOf } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import { CheckIcon } from "@/shared/ui/icons";
import SelectField from "@/shared/ui/select-field";
import { Tabs } from "@/shared/ui/tabs";
import { useStartAction } from "../../model/use-start-action";
import styles from "./style.module.scss";

type CalculatorProps = {
  catalog: ExpertCatalog;
  tariffs: Tariff[];
};

const NOTES = [
  "Документацию прикладываете в PDF, Word или фотографиями — переделывать ничего не нужно.",
  "Эксперта подбираем сами: заявку видят только аттестованные по выбранной области.",
  "Цена берётся из тарифа института и фиксируется в момент подачи заявки.",
];

const Calculator = ({ catalog, tariffs }: CalculatorProps) => {
  const start = useStartAction();
  const [objectCode, setObjectCode] = useState(catalog.objects[0].code);
  const [areaCode, setAreaCode] = useState("");

  const prices = new Map(
    tariffs.map((item) => [tariffKey(item.area_code, item.object_code), item.price]),
  );

  const currentObject = catalog.objects.find((item) => item.code === objectCode);
  const areas = catalog.areas.filter((area) => area.objects.includes(objectCode));

  const price = areaCode === "" ? null : prices.get(tariffKey(areaCode, objectCode)) ?? null;

  const selectObject = (code: string) => {
    setObjectCode(code);
    setAreaCode("");
  };

  const areaOptions = areas.map((area) => {
    const areaPrice = prices.get(tariffKey(area.code, objectCode));

    return {
      value: area.code,
      label: `${area.code} · ${area.title}`,
      hint: areaPrice ? formatRub(areaPrice) : "цена по запросу",
    };
  });

  return (
    <section className={styles.calculator} id="stoimost">
      <div className={styles.heading}>
        <h2 className={styles.title}>Стоимость и срок — до регистрации</h2>
        <p className={styles.lead}>
          Выберите объект и область аттестации: покажем цену из действующего тарифа института.
          Она зафиксируется в заявке и не изменится по ходу работы.
        </p>
      </div>

      <div className={styles.body}>
        <div className={styles.form}>
          <div className={styles.group}>
            <span className={styles.label}>Что проверяем</span>
            <Tabs
              items={catalog.objects.map((item) => ({ key: item.code, label: item.label }))}
              active={objectCode}
              onSelect={selectObject}
              label="Объект экспертизы"
              stretch
            />
            {currentObject && <p className={styles.hint}>{currentObject.title}</p>}
          </div>

          <SelectField
            label="Область аттестации"
            placeholder="Выберите область"
            value={areaCode}
            onChange={setAreaCode}
            options={areaOptions}
          />

          <ul className={styles.notes}>
            {NOTES.map((text) => (
              <li key={text} className={styles.note}>
                <CheckIcon className={styles.noteIcon} />
                <span className={styles.noteText}>{text}</span>
              </li>
            ))}
          </ul>
        </div>

        <aside className={styles.result}>
          <span className={styles.resultLabel}>Стоимость экспертизы</span>
          <span className={styles.resultPrice}>{price ? formatRub(price) : "выберите область"}</span>
          <span className={styles.resultSplit}>
            {price
              ? `Аванс ${formatRub(halfOf(price))}, столько же после готовности заключения`
              : "Оплата двумя частями: аванс и остаток после готовности заключения"}
          </span>

          <dl className={styles.facts}>
            <div className={styles.fact}>
              <dt className={styles.factLabel}>Срок</dt>
              <dd className={styles.factValue}>от 1 дня</dd>
            </div>
            <div className={styles.fact}>
              <dt className={styles.factLabel}>Документ</dt>
              <dd className={styles.factValue}>заключение с ЭЦП</dd>
            </div>
          </dl>

          <Button className={styles.submit} onClick={start}>
            Отправить документацию
          </Button>
        </aside>
      </div>
    </section>
  );
};

export default Calculator;
