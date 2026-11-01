"use client";

import { formatCategory, objectLabel, type ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import TextField from "@/shared/ui/text-field";
import { useCommissionApplication } from "../../model/use-commission-application";
import CertificateBuilder from "./certificate-builder";
import styles from "./style.module.scss";

type ApplicationFormProps = {
  catalog: ExpertCatalog;
  onClose: () => void;
};

const ApplicationForm = ({ catalog, onClose }: ApplicationFormProps) => {
  const application = useCommissionApplication(catalog);
  const { state, canSubmit, changeContact, removeItem, submit } = application;

  if (state.status === "success") {
    return (
      <div className={styles.done}>
        <p className={styles.doneTitle}>Заявка передана в конкурсную комиссию</p>
        <p className={styles.doneText}>
          Спасибо! Комиссия рассмотрит вашу кандидатуру по указанным областям аттестации.
        </p>
        <Button className={styles.submit} onClick={onClose}>
          Закрыть
        </Button>
      </div>
    );
  }

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <TextField
        label="ФИО"
        required
        placeholder="Иванов Иван Иванович"
        maxLength={255}
        autoComplete="name"
        value={state.contacts.fullName}
        onChange={(value) => changeContact("fullName", value)}
      />

      <div className={styles.row}>
        <TextField
          label="Телефон"
          required
          type="tel"
          inputMode="tel"
          placeholder="+7 900 000-00-00"
          maxLength={32}
          autoComplete="tel"
          value={state.contacts.phone}
          onChange={(value) => changeContact("phone", value)}
        />
        <TextField
          label="Email"
          required
          type="email"
          inputMode="email"
          placeholder="name@mail.ru"
          maxLength={320}
          autoComplete="email"
          value={state.contacts.email}
          onChange={(value) => changeContact("email", value)}
        />
      </div>

      <CertificateBuilder catalog={catalog} application={application} />

      {state.items.length === 0 ? (
        <p className={styles.note}>Добавьте хотя бы одну аттестацию.</p>
      ) : (
        <ul className={styles.list}>
          {state.items.map((item) => (
            <li key={item.key} className={styles.item}>
              <span className={styles.code}>{item.areaCode}</span>
              <span className={styles.object}>{objectLabel(catalog, item.objectCode)}</span>
              <span className={styles.meta}>{formatCategory(item.category)}</span>
              <button
                type="button"
                className={styles.remove}
                aria-label="Удалить аттестацию"
                onClick={() => removeItem(item.key)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button
        type="submit"
        className={styles.submit}
        disabled={!canSubmit}
        loading={state.status === "loading"}
      >
        Отправить в конкурсную комиссию
      </Button>
    </form>
  );
};

export default ApplicationForm;
