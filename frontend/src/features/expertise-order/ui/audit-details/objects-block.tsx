import type { AuditObject, AuditScope } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import { EMPTY_OBJECT, type AuditBlockProps } from "../../model/audit-form";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";
import FleetFields from "./fleet-fields";
import { SCOPE_OPTIONS } from "./inputs";
import ObjectFields from "./object-fields";
import styles from "./style.module.scss";

const ObjectsBlock = ({ form, errors, onChange }: AuditBlockProps) => {
  const { scope, objects } = form;

  const selectScope = (value: string) => {
    const shown = value === "one" ? objects.slice(0, 1) : objects;

    onChange({ ...form, scope: value as AuditScope, objects: shown });
  };

  const changeObject = (index: number, item: AuditObject) => {
    const next = objects.map((current, position) => (position === index ? item : current));

    onChange({ ...form, objects: next });
  };

  const addObject = () => onChange({ ...form, objects: [...objects, EMPTY_OBJECT] });

  const removeObject = (index: number) => {
    const next = objects.filter((item, position) => position !== index);

    onChange({ ...form, objects: next });
  };

  return (
    <FieldGroup label="Сведения об объекте аудита">
      <span className={styles.questionLabel}>Масштаб аудита</span>
      <ChipOptions
        label="Масштаб аудита"
        options={SCOPE_OPTIONS}
        value={scope}
        layout="grid"
        invalid={Boolean(errors.scope)}
        onChange={selectScope}
      />

      {scope === "one" && (
        <ObjectFields
          value={objects[0]}
          index={0}
          errors={errors}
          onChange={(item) => changeObject(0, item)}
        />
      )}

      {scope === "all" && <FleetFields form={form} errors={errors} onChange={onChange} />}

      {scope === "selected" &&
        objects.map((item, index) => (
          <div key={index} className={styles.card}>
            <div className={styles.cardHead}>
              <span className={styles.cardTitle}>ОПО {index + 1}</span>
              {objects.length > 1 && (
                <button type="button" className={styles.remove} onClick={() => removeObject(index)}>
                  Удалить
                </button>
              )}
            </div>
            <ObjectFields
              value={item}
              index={index}
              errors={errors}
              onChange={(changed) => changeObject(index, changed)}
            />
          </div>
        ))}

      {scope === "selected" && (
        <Button className={styles.add} onClick={addObject}>
          + Добавить ОПО
        </Button>
      )}
    </FieldGroup>
  );
};

export default ObjectsBlock;
