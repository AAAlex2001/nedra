"use client";

import Link from "next/link";
import type { ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import Modal from "@/shared/ui/modal";
import TextField from "@/shared/ui/text-field";
import { useExpertApplication } from "../../model/use-expert-application";
import CertificateBuilder from "../certificate-builder";
import CertificatesList from "../certificates-list";
import DirectionsPicker from "../directions-picker";
import styles from "../form.module.scss";

const PASSWORD_MIN_LENGTH = 8;

type ExpertApplicationFormProps = {
  catalog: ExpertCatalog;
};

const ExpertApplicationForm = ({ catalog }: ExpertApplicationFormProps) => {
  const {
    state,
    area,
    availableObjects,
    draftComplete,
    canSubmit,
    changeField,
    toggleDirection,
    selectArea,
    selectObject,
    selectCategory,
    changeDate,
    changeNumber,
    addCertificate,
    removeCertificate,
    closeSuccess,
    submit,
  } = useExpertApplication(catalog);

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <Modal open={state.status === "success"} title="Заявка отправлена" onClose={closeSuccess}>
        <p className={styles.successText}>
          Мы проверим удостоверения и свяжемся с вами по почте. Обычно это занимает
          до двух рабочих дней. После одобрения войдите с email и паролем из заявки.
        </p>
      </Modal>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Контактные данные</h2>

        <TextField
          label="Имя и фамилия"
          required
          autoComplete="name"
          placeholder="Иван Иванов"
          minLength={2}
          maxLength={255}
          value={state.fields.fullName}
          onChange={(value) => changeField("fullName", value)}
        />

        <div className={styles.row}>
          <TextField
            label="Email"
            required
            type="email"
            inputMode="email"
            autoComplete="email"
            placeholder="mail@example.com"
            value={state.fields.email}
            onChange={(value) => changeField("email", value)}
          />
          <TextField
            label="Телефон"
            required
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="+7 999 000-00-00"
            minLength={10}
            maxLength={32}
            value={state.fields.phone}
            onChange={(value) => changeField("phone", value)}
          />
        </div>

        <TextField
          label="Пароль для входа"
          required
          type="password"
          autoComplete="new-password"
          placeholder="Не короче 8 символов"
          minLength={PASSWORD_MIN_LENGTH}
          maxLength={72}
          value={state.fields.password}
          onChange={(value) => changeField("password", value)}
        />
        <p className={styles.hint}>
          Минимум 8 символов, хотя бы одна буква и одна цифра. Пароль понадобится после
          одобрения заявки.
        </p>
      </section>

      <section className={styles.section}>
        <DirectionsPicker
          directions={catalog.directions}
          selected={state.directions}
          onToggle={toggleDirection}
        />
        <p className={styles.hint}>Можно выбрать несколько направлений.</p>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Удостоверения</h2>
        <p className={styles.sectionText}>
          Для каждого удостоверения укажите область аттестации, объект экспертизы,
          категорию, срок действия и номер удостоверения или регистрации в ЕРУЛ.
        </p>

        <CertificateBuilder
          catalog={catalog}
          draft={state.draft}
          area={area}
          availableObjects={availableObjects}
          complete={draftComplete}
          onArea={selectArea}
          onObject={selectObject}
          onCategory={selectCategory}
          onDate={changeDate}
          onNumber={changeNumber}
          onAdd={addCertificate}
        />

        <CertificatesList
          catalog={catalog}
          items={state.certificates}
          onRemove={removeCertificate}
        />
      </section>

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button
        type="submit"
        className={styles.submit}
        disabled={!canSubmit}
        loading={state.status === "loading"}
      >
        Отправить заявку
      </Button>

      <p className={styles.consent}>
        Нажимая кнопку, вы соглашаетесь с{" "}
        <Link href="/politika-konfidencialnosti" className={styles.consentLink}>
          политикой конфиденциальности
        </Link>
        .
      </p>
    </form>
  );
};

export default ExpertApplicationForm;
