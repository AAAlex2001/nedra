"use client";

import { useState } from "react";
import { areaTitle, objectLabel, type ExpertCatalog } from "@/entities/expert";
import { EXPERTISE_STATUS_LABELS, type ExpertiseStatus } from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { keepDigits } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useExpertises } from "../../model/use-expertises";
import type { ExpertiseAdminRecord } from "../../model/types";
import styles from "./style.module.scss";

type ExpertisesListProps = {
  initialItems: ExpertiseAdminRecord[];
  catalog: ExpertCatalog | null;
  basePath: string;
};

type ExpertiseRowProps = {
  expertise: ExpertiseAdminRecord;
  catalog: ExpertCatalog | null;
  pending: boolean;
  onSave: (id: number, status: ExpertiseStatus, price: string | null) => void;
  onRemove: (id: number) => void;
};

const STATUSES = Object.keys(EXPERTISE_STATUS_LABELS) as ExpertiseStatus[];

const toWhole = (price: string | null): string =>
  price === null ? "" : String(Math.round(Number(price)));

const ExpertiseRow = ({ expertise, catalog, pending, onSave, onRemove }: ExpertiseRowProps) => {
  const [status, setStatus] = useState<ExpertiseStatus>(expertise.status);
  const [price, setPrice] = useState(toWhole(expertise.price));

  const selectStatus = (value: string) => {
    const found = STATUSES.find((item) => item === value);

    if (found) setStatus(found);
  };

  const remove = () => {
    if (window.confirm(`Удалить заявку №${expertise.id} вместе с файлами?`)) {
      onRemove(expertise.id);
    }
  };

  return (
    <article className={styles.card}>
      <header className={styles.head}>
        <span className={styles.id}>№{expertise.id}</span>
        <time className={styles.date} dateTime={expertise.created_at}>
          {formatRequestDate(expertise.created_at)}
        </time>
        <span className={styles.badge}>
          {catalog ? objectLabel(catalog, expertise.object_code) : expertise.object_code}
        </span>
        <span className={styles.area}>
          {expertise.area_code}
          {catalog && ` · ${areaTitle(catalog, expertise.area_code)}`}
        </span>
      </header>

      <dl className={styles.details}>
        <div className={styles.detail}>
          <dt className={styles.term}>Заказчик</dt>
          <dd className={styles.value}>{expertise.customer_name}</dd>
        </div>
        <div className={styles.detail}>
          <dt className={styles.term}>Эксперт</dt>
          <dd className={styles.value}>{expertise.expert_name ?? "не назначен"}</dd>
        </div>
        <div className={styles.detail}>
          <dt className={styles.term}>Категория</dt>
          <dd className={styles.value}>{expertise.expert_category}</dd>
        </div>
      </dl>

      {expertise.comment && <p className={styles.comment}>{expertise.comment}</p>}

      <div className={styles.fields}>
        <SelectField
          label="Статус"
          placeholder="Выберите статус"
          value={status}
          onChange={selectStatus}
          options={STATUSES.map((item) => ({
            value: item,
            label: EXPERTISE_STATUS_LABELS[item],
          }))}
        />
        <TextField
          label="Стоимость, ₽"
          inputMode="numeric"
          placeholder="не задана"
          value={price}
          onChange={(value) => setPrice(keepDigits(value))}
        />
      </div>

      <div className={styles.buttons}>
        <button type="button" className={styles.remove} disabled={pending} onClick={remove}>
          Удалить
        </button>
        <Button
          loading={pending}
          onClick={() => onSave(expertise.id, status, price === "" ? null : price)}
        >
          Сохранить
        </Button>
      </div>
    </article>
  );
};

const ExpertisesList = ({ initialItems, catalog, basePath }: ExpertisesListProps) => {
  const { items, pendingId, refreshing, error, save, remove, refresh } = useExpertises(
    initialItems,
    basePath,
  );

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <span className={styles.count}>Всего заявок: {items.length}</span>
        <Button loading={refreshing} onClick={() => void refresh()}>
          Обновить
        </Button>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {items.length === 0 ? (
        <p className={styles.empty}>Заявок на экспертизу пока нет.</p>
      ) : (
        <div className={styles.list}>
          {items.map((item) => (
            <ExpertiseRow
              key={item.id}
              expertise={item}
              catalog={catalog}
              pending={pendingId === item.id}
              onSave={(id, status, price) => void save(id, status, price)}
              onRemove={(id) => void remove(id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ExpertisesList;
