import { CONTRACT_KIND_LABELS, type ContractKind } from "@/entities/expertise";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";

type KindSectionProps = {
  kinds: ContractKind[];
  value: ContractKind | "";
  onSelect: (kind: ContractKind | "") => void;
};

const KindSection = ({ kinds, value, onSelect }: KindSectionProps) => {
  const options = [
    ...kinds.map((kind) => ({ value: kind, label: CONTRACT_KIND_LABELS[kind] })),
    { value: "" as const, label: "Не знаю" },
  ];

  const note = value
    ? "По виду проекта подберём договор."
    : "Вид проекта определит эксперт, а вам останется согласиться с договором.";

  return (
    <FieldGroup label="Вид проекта" note={note}>
      <ChipOptions
        label="Вид проекта"
        layout="wrap"
        options={options}
        value={value}
        onChange={onSelect}
      />
    </FieldGroup>
  );
};

export default KindSection;
