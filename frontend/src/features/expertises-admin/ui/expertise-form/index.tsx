"use client";

import { useState } from "react";
import {
  AUDIT_STATUS_LABELS,
  CONTRACT_KIND_LABELS,
  EXPERTISE_STATUS_LABELS,
  type ContractKind,
  type ExpertiseStatus,
} from "@/entities/expertise";
import { keepDigits } from "@/shared/lib/text";
import Button from "@/shared/ui/button";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import type { ExpertiseDraft, ExpertOption } from "../../model/types";
import styles from "./style.module.scss";

type ExpertiseFormProps = {
  draft: ExpertiseDraft;
  audit: boolean;
  experts: ExpertOption[];
  contractKinds: ContractKind[];
  pending: boolean;
  onSave: (draft: ExpertiseDraft) => void;
  onCancel: () => void;
};

const STATUSES = Object.keys(EXPERTISE_STATUS_LABELS) as ExpertiseStatus[];

const AUDIT_ONLY: ExpertiseStatus[] = ["consultation", "offer", "counter", "plan", "plan_review"];

const ExpertiseForm = ({
  draft,
  audit,
  experts,
  contractKinds,
  pending,
  onSave,
  onCancel,
}: ExpertiseFormProps) => {
  const labels = audit ? AUDIT_STATUS_LABELS : EXPERTISE_STATUS_LABELS;
  const statuses = audit ? STATUSES : STATUSES.filter((item) => !AUDIT_ONLY.includes(item));
  const [status, setStatus] = useState(draft.status);
  const [price, setPrice] = useState(draft.price);
  const [expertId, setExpertId] = useState(draft.expertId);
  const [contractKind, setContractKind] = useState(draft.contractKind);

  const selectStatus = (value: string) => {
    const found = statuses.find((item) => item === value);

    if (found) setStatus(found);
  };

  const selectKind = (value: string) => {
    const found = contractKinds.find((item) => item === value);

    if (found) setContractKind(found);
  };

  const expertOptions = [
    { value: "", label: "Не назначен" },
    ...experts.map((expert) => ({ value: String(expert.user_id), label: expert.full_name })),
  ];

  const kindOptions = contractKinds.map((kind) => ({
    value: kind,
    label: CONTRACT_KIND_LABELS[kind],
  }));

  const save = () => onSave({ status, price, expertId, contractKind });

  return (
    <div className={styles.form}>
      <div className={styles.fields}>
        <SelectField
          label="Статус"
          placeholder="Выберите статус"
          value={status}
          onChange={selectStatus}
          options={statuses.map((item) => ({
            value: item,
            label: labels[item],
          }))}
        />
        <TextField
          label="Стоимость, ₽"
          inputMode="numeric"
          placeholder="не задана"
          value={price}
          onChange={(value) => setPrice(keepDigits(value))}
        />
        <SelectField
          label="Эксперт"
          placeholder="Не назначен"
          value={expertId}
          onChange={setExpertId}
          options={expertOptions}
        />
        {kindOptions.length > 1 && (
          <SelectField
            label="Вид договора"
            placeholder="Определит эксперт"
            value={contractKind}
            onChange={selectKind}
            options={kindOptions}
          />
        )}
      </div>

      {audit && draft.status === "consultation" && (
        <p className={styles.hint}>
          После консультации поставьте статус «Ждёт аудитора»: заявку увидят руководители
          аудиторских групп.
        </p>
      )}

      <div className={styles.buttons}>
        <button type="button" className={styles.cancel} disabled={pending} onClick={onCancel}>
          Отмена
        </button>
        <Button loading={pending} onClick={save}>
          Сохранить
        </Button>
      </div>
    </div>
  );
};

export default ExpertiseForm;
