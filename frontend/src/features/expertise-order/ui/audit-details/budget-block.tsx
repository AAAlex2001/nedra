import type { BudgetMode, Negotiation } from "@/entities/expertise";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import type { AuditBlockProps } from "../../model/audit-form";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";
import { BUDGET_OPTIONS, NEGOTIATION_OPTIONS } from "./inputs";
import styles from "./style.module.scss";

type BudgetBlockProps = AuditBlockProps & {
  price: string;
  onPriceChange: (value: string) => void;
};

const BudgetBlock = ({ form, errors, onChange, price, onPriceChange }: BudgetBlockProps) => (
  <FieldGroup label="Стоимость">
    <SelectField
      label="Планируемый бюджет / Целевая стоимость аудита"
      placeholder="Выберите вариант"
      required
      options={BUDGET_OPTIONS}
      value={form.budget}
      onChange={(value) => onChange({ ...form, budget: value as BudgetMode })}
    />

    {form.budget === "custom" && (
      <TextField
        label="Своя сумма, ₽"
        required
        inputMode="numeric"
        placeholder="Не менее 100 000"
        maxLength={14}
        invalid={Boolean(errors.price)}
        value={price}
        onChange={onPriceChange}
      />
    )}

    <span className={styles.questionLabel}>Возможность обсуждения стоимости (торг)</span>
    <ChipOptions
      label="Возможность обсуждения стоимости"
      options={NEGOTIATION_OPTIONS}
      value={form.negotiation}
      layout="grid"
      invalid={Boolean(errors.negotiation)}
      onChange={(negotiation) => onChange({ ...form, negotiation: negotiation as Negotiation })}
    />
  </FieldGroup>
);

export default BudgetBlock;
