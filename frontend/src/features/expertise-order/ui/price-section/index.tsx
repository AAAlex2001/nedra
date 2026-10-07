import TextField from "@/shared/ui/text-field";
import FieldGroup from "../field-group";

type PriceSectionProps = {
  label: string;
  executors: string;
  value: string;
  onChange: (value: string) => void;
};

const PriceSection = ({ label, executors, value, onChange }: PriceSectionProps) => (
  <FieldGroup
    note={`${executors} увидят цену и возьмут заявку, если согласны с ней. Эта сумма войдёт в договор, оплата — двумя частями по 50 %.`}
  >
    <TextField
      label={label}
      required
      inputMode="numeric"
      placeholder="Например, 50 000"
      maxLength={14}
      value={value}
      onChange={onChange}
    />
  </FieldGroup>
);

export default PriceSection;
