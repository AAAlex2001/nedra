"use client";

import Link from "next/link";
import type { ExpertCatalog } from "@/entities/expert";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import FilesField from "@/shared/ui/files-field";
import Modal from "@/shared/ui/modal";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useExpertiseOrder } from "../../model/use-expertise-order";
import styles from "./style.module.scss";

type OrderFormProps = {
  catalog: ExpertCatalog;
};

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const OrderForm = ({ catalog }: OrderFormProps) => {
  const {
    state,
    currentObject,
    availableAreas,
    selectedArea,
    requiredCategory,
    canSubmit,
    selectObject,
    setMode,
    selectHazard,
    selectCategory,
    selectArea,
    addFiles,
    removeFile,
    changeComment,
    closeSuccess,
    submit,
  } = useExpertiseOrder(catalog);

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
          Эксперты, аттестованные по вашей области, получили уведомление. Когда кто-то из них
          возьмёт заявку в работу, вы увидите это в{" "}
          <Link href="/kabinet" className={styles.successLink}>
            личном кабинете
          </Link>
          .
        </p>
      </Modal>

      <div className={styles.group}>
        <span className={styles.label}>Что проверяем</span>
        <div className={styles.segments} role="tablist" aria-label="Объект экспертизы">
          {catalog.objects.map((object) => (
            <button
              key={object.code}
              type="button"
              role="tab"
              aria-selected={state.objectCode === object.code}
              title={object.title}
              className={`${styles.segment} ${state.objectCode === object.code ? styles.segmentActive : ""}`}
              onClick={() => selectObject(object.code)}
            >
              {object.label}
            </button>
          ))}
        </div>
        {currentObject && <p className={styles.note}>{currentObject.title}</p>}
      </div>

      <div className={styles.group}>
        <span className={styles.label}>Требования к эксперту</span>
        <div className={styles.segments} role="tablist" aria-label="Как задать требование">
          <button
            type="button"
            role="tab"
            aria-selected={state.mode === "hazard"}
            className={`${styles.segment} ${state.mode === "hazard" ? styles.segmentActive : ""}`}
            onClick={() => setMode("hazard")}
          >
            Класс опасности ОПО
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={state.mode === "category"}
            className={`${styles.segment} ${state.mode === "category" ? styles.segmentActive : ""}`}
            onClick={() => setMode("category")}
          >
            Категория эксперта
          </button>
        </div>

        {state.mode === "hazard" ? (
          <div className={styles.row} role="group" aria-label="Класс опасности">
            {catalog.hazard_classes.map((rule) => (
              <Chip
                key={rule.hazard_class}
                active={state.hazardClass === rule.hazard_class}
                className={styles.rowChip}
                onClick={() => selectHazard(rule.hazard_class)}
              >
                {rule.hazard_class} класс
              </Chip>
            ))}
          </div>
        ) : (
          <div className={styles.row} role="group" aria-label="Категория эксперта">
            {catalog.categories.map((category) => (
              <Chip
                key={category}
                active={state.category === category}
                className={styles.rowChip}
                onClick={() => selectCategory(category)}
              >
                {category} категория
              </Chip>
            ))}
          </div>
        )}

        <p className={styles.note}>
          {requiredCategory === null
            ? "Класс опасности указан в свидетельстве о регистрации ОПО. По нему подберём категорию эксперта."
            : `Заявку увидят эксперты ${requiredCategory} категории и выше.`}
        </p>
      </div>

      <div className={styles.group}>
        <div className={styles.areaSelect}>
          <SelectField
            label="Область аттестации"
            placeholder="Выберите отрасль"
            required
            value={state.areaCode}
            onChange={selectArea}
            options={availableAreas.map((area) => ({
              value: area.code,
              label: area.code,
              hint: area.title,
            }))}
          />
        </div>

        <div className={styles.areaChips}>
          <span className={styles.label}>
            Область аттестации<span className={styles.required}> *</span>
          </span>
          <div className={styles.chips} role="group" aria-label="Область аттестации">
            {catalog.areas.map((area) => {
              const allowed = availableAreas.some((item) => item.code === area.code);

              return (
                <Chip
                  key={area.code}
                  active={state.areaCode === area.code}
                  disabled={!allowed}
                  title={area.title}
                  onClick={() => selectArea(area.code)}
                >
                  {area.code}
                </Chip>
              );
            })}
          </div>
          <p className={styles.note}>
            {selectedArea ? selectedArea.title : "Выберите отрасль, к которой относится объект."}
          </p>
        </div>
      </div>

      <FilesField
        label="Документация"
        required
        files={state.files}
        accept={ACCEPT}
        hint="PDF, Word, JPG или PNG, до 50 МБ каждый. Можно приложить несколько файлов."
        onAdd={addFiles}
        onRemove={removeFile}
      />

      <TextField
        label="Комментарий"
        multiline
        placeholder="Что важно знать эксперту: сроки, особенности объекта, на что обратить внимание"
        maxLength={4000}
        value={state.comment}
        onChange={changeComment}
      />

      {state.error && <p className={styles.error}>{state.error}</p>}

      <Button
        type="submit"
        className={styles.submit}
        disabled={!canSubmit}
        loading={state.status === "loading"}
      >
        Отправить на экспертизу
      </Button>
    </form>
  );
};

export default OrderForm;
