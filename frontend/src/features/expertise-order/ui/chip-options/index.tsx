import classNames from "classnames";
import Chip from "@/shared/ui/chip";
import styles from "./style.module.scss";

type ChipOption = {
  value: string;
  label: string;
  title?: string;
  disabled?: boolean;
};

type ChipOptionsProps = {
  label: string;
  options: ChipOption[];
  value: string | null;
  layout: "row" | "wrap" | "grid";
  invalid?: boolean;
  onChange: (value: string) => void;
};

const ChipOptions = ({ label, options, value, layout, invalid, onChange }: ChipOptionsProps) => (
  <div className={classNames(styles[layout], invalid && styles.invalid)} role="group" aria-label={label}>
    {options.map((option) => (
      <Chip
        key={option.value}
        active={option.value === value}
        disabled={option.disabled}
        title={option.title}
        className={styles.option}
        onClick={() => onChange(option.value)}
      >
        {option.label}
      </Chip>
    ))}
  </div>
);

export type { ChipOption };

export default ChipOptions;
