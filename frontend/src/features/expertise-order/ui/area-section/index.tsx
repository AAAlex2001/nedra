import type { AttestationArea } from "@/entities/expert";
import SelectField from "@/shared/ui/select-field";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";
import styles from "./style.module.scss";

type AreaSectionProps = {
  areas: AttestationArea[];
  available: AttestationArea[];
  value: string;
  onSelect: (code: string) => void;
};

const UNKNOWN_OPTIONS = [
  { value: "", label: "Не знаю", title: "Эксперт определит область по документации" },
];

const UNKNOWN_NOTE = "Если не знаете отрасль, оставьте «Не знаю» — определим по документации.";

const AreaSection = ({ areas, available, value, onSelect }: AreaSectionProps) => {
  const selected = available.find((area) => area.code === value);

  const selectOptions = available.map((area) => ({
    value: area.code,
    label: area.code,
    hint: area.title,
  }));

  const chipOptions = areas.map((area) => ({
    value: area.code,
    label: area.code,
    title: area.title,
    disabled: !available.some((item) => item.code === area.code),
  }));

  return (
    <FieldGroup note={selected ? selected.title : UNKNOWN_NOTE}>
      <div className={styles.select}>
        <SelectField
          label="Область аттестации"
          placeholder="Выберите отрасль"
          value={value}
          onChange={onSelect}
          options={selectOptions}
        />
      </div>

      <div className={styles.chips}>
        <FieldGroup label="Область аттестации">
          <ChipOptions
            label="Область аттестации"
            layout="wrap"
            options={chipOptions}
            value={value}
            onChange={onSelect}
          />
        </FieldGroup>
      </div>

      <ChipOptions
        label="Область не известна"
        layout="row"
        options={UNKNOWN_OPTIONS}
        value={value}
        onChange={onSelect}
      />
    </FieldGroup>
  );
};

export default AreaSection;
