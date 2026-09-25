"use client";

import { useState } from "react";
import { areaTitle, objectLabel, type ExpertCatalog } from "@/entities/expert";
import {
  CONTRACT_KIND_LABELS,
  DEADLINE_LABELS,
  EXPERTISE_STATUS_LABELS,
  type ExpertiseStatus,
} from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import { statusGroup } from "../../model/groups";
import type { ExpertiseAdminRecord } from "../../model/types";
import ExpertiseForm from "../expertise-form";
import styles from "./style.module.scss";

type ExpertiseCardProps = {
  expertise: ExpertiseAdminRecord;
  catalog: ExpertCatalog | null;
  pending: boolean;
  onSave: (id: number, status: ExpertiseStatus, price: string | null) => void;
  onRemove: (id: number) => void;
};

type FactProps = {
  label: string;
  value: string;
};

const Fact = ({ label, value }: FactProps) => (
  <div className={styles.fact}>
    <dt className={styles.term}>{label}</dt>
    <dd className={styles.value}>{value}</dd>
  </div>
);

const ExpertiseCard = ({ expertise, catalog, pending, onSave, onRemove }: ExpertiseCardProps) => {
  const [editing, setEditing] = useState(false);

  let subject = "Область определит эксперт";
  if (expertise.area_code) {
    subject = catalog ? areaTitle(catalog, expertise.area_code) : expertise.area_code;
  }

  let object = "";
  if (expertise.object_code) {
    object = catalog ? objectLabel(catalog, expertise.object_code) : expertise.object_code;
  }

  const save = (status: ExpertiseStatus, price: string | null) => {
    onSave(expertise.id, status, price);
    setEditing(false);
  };

  const remove = () => {
    if (window.confirm(`Удалить заявку №${expertise.id} вместе с файлами?`)) {
      onRemove(expertise.id);
    }
  };

  return (
    <article className={styles.card}>
      <header className={styles.head}>
        <div className={styles.headline}>
          <span className={styles.id}>№{expertise.id}</span>
          <time className={styles.date} dateTime={expertise.created_at}>
            {formatRequestDate(expertise.created_at)}
          </time>
        </div>

        <span className={`${styles.status} ${styles[statusGroup(expertise.status)]}`}>
          {EXPERTISE_STATUS_LABELS[expertise.status]}
        </span>
      </header>

      <h3 className={styles.subject}>{subject}</h3>

      <div className={styles.chips}>
        {expertise.area_code && <span className={styles.chip}>{expertise.area_code}</span>}
        {object && <span className={styles.chip}>{object}</span>}
        {expertise.expert_category !== null && (
          <span className={styles.chip}>Категория {expertise.expert_category}</span>
        )}
        {expertise.hazard_class !== null && (
          <span className={styles.chip}>Класс опасности {expertise.hazard_class}</span>
        )}
        {expertise.deadline && (
          <span className={styles.chip}>Срок: {DEADLINE_LABELS[expertise.deadline]}</span>
        )}
      </div>

      <dl className={styles.facts}>
        <Fact label="Заказчик" value={expertise.customer_name} />
        {expertise.company && (
          <Fact
            label="Организация"
            value={`${expertise.company.name}, ИНН ${expertise.company.inn}`}
          />
        )}
        {expertise.object_name && <Fact label="Документация" value={expertise.object_name} />}
        <Fact
          label="Вид договора"
          value={
            expertise.contract_kind
              ? CONTRACT_KIND_LABELS[expertise.contract_kind]
              : "определит эксперт"
          }
        />
        <Fact label="Эксперт" value={expertise.expert_name ?? "не назначен"} />
        <Fact
          label="Стоимость"
          value={expertise.price === null ? "не задана" : formatRub(expertise.price)}
        />
      </dl>

      {expertise.comment && <p className={styles.comment}>{expertise.comment}</p>}

      {editing ? (
        <ExpertiseForm
          status={expertise.status}
          price={expertise.price}
          pending={pending}
          onSave={save}
          onCancel={() => setEditing(false)}
        />
      ) : (
        <div className={styles.buttons}>
          <button type="button" className={styles.remove} disabled={pending} onClick={remove}>
            Удалить
          </button>
          <button
            type="button"
            className={styles.edit}
            disabled={pending}
            onClick={() => setEditing(true)}
          >
            Изменить
          </button>
        </div>
      )}
    </article>
  );
};

export default ExpertiseCard;
