"use client";

import Link from "next/link";
import type { ExpertCatalog } from "@/entities/expert";
import { CONTRACT_KIND_LABELS } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Chip from "@/shared/ui/chip";
import FilesField from "@/shared/ui/files-field";
import Modal from "@/shared/ui/modal";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import { useExpertiseOrder } from "../../model/use-expertise-order";
import type { CompanyField, Deadline } from "../../model/types";
import styles from "./style.module.scss";

type OrderFormProps = {
  catalog: ExpertCatalog;
};

type CompanyInput = {
  field: CompanyField;
  label: string;
  placeholder: string;
  numeric?: boolean;
  optional?: boolean;
  wide?: boolean;
};

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const COMPANY_INPUTS: CompanyInput[] = [
  {
    field: "full_name",
    label: "Полное наименование",
    placeholder: "Общество с ограниченной ответственностью «Ромашка»",
    wide: true,
  },
  { field: "name", label: "Сокращённое наименование", placeholder: "ООО «Ромашка»" },
  { field: "inn", label: "ИНН", placeholder: "10 или 12 цифр", numeric: true },
  { field: "kpp", label: "КПП", placeholder: "Если есть", numeric: true, optional: true },
  { field: "ogrn", label: "ОГРН или ОГРНИП", placeholder: "13 или 15 цифр", numeric: true },
  {
    field: "address",
    label: "Юридический адрес",
    placeholder: "630000, г. Новосибирск, ул. Ленина, д. 1",
    wide: true,
  },
  { field: "bank", label: "Банк", placeholder: "АО «Альфа-Банк»", wide: true },
  { field: "bic", label: "БИК", placeholder: "9 цифр", numeric: true },
  { field: "account", label: "Расчётный счёт", placeholder: "20 цифр", numeric: true },
  { field: "corr_account", label: "Корреспондентский счёт", placeholder: "20 цифр", numeric: true },
  { field: "signer_position", label: "Должность подписанта", placeholder: "Генеральный директор" },
  { field: "signer_name", label: "ФИО подписанта", placeholder: "Иванов Иван Иванович" },
  {
    field: "signer_genitive",
    label: "В лице кого",
    placeholder: "генерального директора Иванова Ивана Ивановича",
    wide: true,
  },
  { field: "signer_basis", label: "Действует на основании", placeholder: "Устава" },
];

const DEADLINES: { value: Deadline; label: string }[] = [
  { value: "today", label: "Сегодня" },
  { value: "three_days", label: "До 3 дней" },
  { value: "week", label: "Неделя" },
  { value: "any", label: "Неважно" },
];

const OrderForm = ({ catalog }: OrderFormProps) => {
  const {
    state,
    currentObject,
    availableAreas,
    selectedArea,
    contractKinds,
    requiredCategory,
    canSubmit,
    selectObject,
    selectKind,
    changeObjectName,
    setMode,
    selectHazard,
    selectCategory,
    selectArea,
    selectDeadline,
    changeCompany,
    addFiles,
    removeFile,
    setCard,
    removeCard,
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
          Эксперты получили уведомление. Когда кто-то из них возьмёт заявку в работу, вы увидите
          это в{" "}
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
          <button
            type="button"
            role="tab"
            aria-selected={state.objectCode === ""}
            title="Эксперт определит по документации"
            className={`${styles.segment} ${state.objectCode === "" ? styles.segmentActive : ""}`}
            onClick={() => selectObject("")}
          >
            Не знаю
          </button>
        </div>
        <p className={styles.note}>
          {currentObject
            ? currentObject.title
            : "Ничего страшного: эксперт определит объект по вашей документации."}
        </p>
      </div>

      {contractKinds.length > 1 && (
        <div className={styles.group}>
          <span className={styles.label}>Вид проекта</span>
          <div className={styles.chips} role="group" aria-label="Вид проекта">
            {contractKinds.map((kind) => (
              <Chip
                key={kind}
                active={state.contractKind === kind}
                onClick={() => selectKind(kind)}
              >
                {CONTRACT_KIND_LABELS[kind]}
              </Chip>
            ))}
            <Chip active={state.contractKind === ""} onClick={() => selectKind("")}>
              Не знаю
            </Chip>
          </div>
          <p className={styles.note}>
            {state.contractKind
              ? "По виду проекта подберём договор."
              : "Вид проекта определит эксперт, а вам останется согласиться с договором."}
          </p>
        </div>
      )}

      <TextField
        label="Наименование документации"
        required
        placeholder="Как на титульном листе проекта"
        maxLength={500}
        value={state.objectName}
        onChange={changeObjectName}
      />

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
          <button
            type="button"
            role="tab"
            aria-selected={state.mode === "unknown"}
            className={`${styles.segment} ${state.mode === "unknown" ? styles.segmentActive : ""}`}
            onClick={() => setMode("unknown")}
          >
            Не знаю
          </button>
        </div>

        {state.mode === "hazard" && (
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
        )}

        {state.mode === "category" && (
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
          {state.mode === "unknown"
            ? "Заявку увидят все аттестованные эксперты, подходящего подберём по документации."
            : requiredCategory === null
              ? "Класс опасности указан в свидетельстве о регистрации ОПО. По нему подберём категорию эксперта."
              : `Заявку увидят эксперты ${requiredCategory} категории и выше.`}
        </p>
      </div>

      <div className={styles.group}>
        <div className={styles.areaSelect}>
          <SelectField
            label="Область аттестации"
            placeholder="Выберите отрасль"
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
          <span className={styles.label}>Область аттестации</span>
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
        </div>

        <div className={styles.row}>
          <Chip
            active={state.areaCode === ""}
            className={styles.rowChip}
            title="Эксперт определит область по документации"
            onClick={() => selectArea("")}
          >
            Не знаю
          </Chip>
        </div>

        <p className={styles.note}>
          {selectedArea
            ? selectedArea.title
            : "Если не знаете отрасль, оставьте «Не знаю» — определим по документации."}
        </p>
      </div>

      <div className={styles.group}>
        <span className={styles.label}>Когда нужно заключение</span>
        <div className={styles.row} role="group" aria-label="Срок">
          {DEADLINES.map((item) => (
            <Chip
              key={item.value}
              active={state.deadline === item.value}
              className={styles.rowChip}
              onClick={() => selectDeadline(item.value)}
            >
              {item.label}
            </Chip>
          ))}
        </div>
        <p className={styles.note}>
          Срок влияет на подбор эксперта: чем он короче, тем меньше специалистов смогут взять
          заявку.
        </p>
      </div>

      <FilesField
        label="Документация"
        required
        files={state.files}
        accept={ACCEPT}
        hint="PDF, Word, JPG или PNG, до 50 МБ каждый. Можно приложить несколько файлов. Если документации нет — приложите техническое задание."
        onAdd={addFiles}
        onRemove={removeFile}
      />

      <div className={styles.group}>
        <span className={styles.label}>Реквизиты заказчика</span>
        <p className={styles.note}>
          По ним составим договор, счёт и акт. Заявки можно подавать от разных организаций —
          реквизиты указываются в каждой.
        </p>
        <div className={styles.fields}>
          {COMPANY_INPUTS.map((input) => (
            <div key={input.field} className={input.wide ? styles.wide : undefined}>
              <TextField
                label={input.label}
                required={!input.optional}
                placeholder={input.placeholder}
                inputMode={input.numeric ? "numeric" : undefined}
                maxLength={500}
                value={state.company[input.field]}
                onChange={(value) => changeCompany(input.field, value)}
              />
            </div>
          ))}
        </div>
      </div>

      <FilesField
        label="Карточка организации"
        files={state.companyCard ? [state.companyCard] : []}
        accept={ACCEPT}
        hint="Приложите карточку с реквизитами, чтобы бухгалтерия сверила данные."
        onAdd={setCard}
        onRemove={removeCard}
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
