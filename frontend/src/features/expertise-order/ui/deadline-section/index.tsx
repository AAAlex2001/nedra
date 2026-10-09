import type { Deadline } from "../../model/types";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";

type DeadlineSectionProps = {
  label: string;
  executor: string;
  value: Deadline | null;
  onSelect: (value: Deadline) => void;
};

const DEADLINES: { value: Deadline; label: string }[] = [
  { value: "today", label: "Сегодня" },
  { value: "three_days", label: "До 3 дней" },
  { value: "week", label: "Неделя" },
  { value: "any", label: "Неважно" },
];

const DeadlineSection = ({ label, executor, value, onSelect }: DeadlineSectionProps) => (
  <FieldGroup
    label={label}
    note={`Срок влияет на подбор ${executor}: чем он короче, тем меньше специалистов смогут взять заявку.`}
  >
    <ChipOptions
      label="Срок"
      layout="row"
      options={DEADLINES}
      value={value}
      onChange={(deadline) => onSelect(deadline as Deadline)}
    />
  </FieldGroup>
);

export default DeadlineSection;
