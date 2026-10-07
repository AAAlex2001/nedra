import Chip from "@/shared/ui/chip";
import styles from "./style.module.scss";

type ChipOption<T extends string | number> = {
  value: T;
  label: string;
  title?: string;
  disabled?: boolean;
};

type ChipOptionsProps<T extends string | number> = {
  label: string;
  options: ChipOption<T>[];
  value: T | null;
  layout: "row" | "wrap";
  onChange: (value: T) => void;
};

const ChipOptions = <T extends string | number>({
  label,
  options,
  value,
  layout,
  onChange,
}: ChipOptionsProps<T>) => (
  <div className={styles[layout]} role="group" aria-label={label}>
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
