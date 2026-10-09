import classNames from "classnames";
import type { AuditObject, HazardClass, HazardSign } from "@/entities/expertise";
import Checkbox from "@/shared/ui/checkbox";
import TextField from "@/shared/ui/text-field";
import type { FormErrors } from "../../model/types";
import ChipOptions from "../chip-options";
import { HAZARD_CLASS_OPTIONS, HAZARD_SIGN_OPTIONS, OBJECT_INPUTS } from "./inputs";
import styles from "./style.module.scss";

type ObjectFieldsProps = {
  value: AuditObject;
  index: number;
  errors: FormErrors;
  onChange: (value: AuditObject) => void;
};

const ObjectFields = ({ value, index, errors, onChange }: ObjectFieldsProps) => {
  const hasError = (field: string): boolean => Boolean(errors[`object-${index}-${field}`]);

  const toggleSign = (sign: HazardSign) => {
    const chosen = value.hazard_signs.includes(sign);
    const signs = chosen
      ? value.hazard_signs.filter((item) => item !== sign)
      : [...value.hazard_signs, sign];

    onChange({ ...value, hazard_signs: signs });
  };

  return (
    <div className={styles.fields}>
      {OBJECT_INPUTS.map((input) => (
        <div key={input.field} className={input.wide ? styles.wide : undefined}>
          <TextField
            label={input.label}
            required
            placeholder={input.placeholder}
            maxLength={500}
            invalid={hasError(input.field)}
            value={value[input.field]}
            onChange={(text) => onChange({ ...value, [input.field]: text })}
          />
        </div>
      ))}

      <div className={classNames(styles.question, styles.wide)}>
        <span className={styles.questionLabel}>Класс опасности ОПО</span>
        <ChipOptions
          label="Класс опасности ОПО"
          options={HAZARD_CLASS_OPTIONS}
          value={value.hazard_class || null}
          layout="row"
          invalid={hasError("hazard_class")}
          onChange={(hazardClass) => onChange({ ...value, hazard_class: hazardClass as HazardClass })}
        />
      </div>

      <div className={classNames(styles.question, styles.wide)}>
        <span className={styles.questionLabel}>Признаки опасности ОПО</span>
        <div className={classNames(styles.checks, hasError("hazard_signs") && styles.checksInvalid)}>
          {HAZARD_SIGN_OPTIONS.map((option) => (
            <Checkbox
              key={option.value}
              checked={value.hazard_signs.includes(option.value)}
              onChange={() => toggleSign(option.value)}
            >
              {option.label}
            </Checkbox>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ObjectFields;
