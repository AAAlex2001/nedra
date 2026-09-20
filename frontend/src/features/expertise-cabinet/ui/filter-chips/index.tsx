import Chip from "@/shared/ui/chip";
import styles from "./style.module.scss";

type FilterOption = {
  value: string;
  label: string;
};

type FilterChipsProps = {
  label: string;
  allLabel: string;
  options: FilterOption[];
  value: string;
  onSelect: (value: string) => void;
};

const FilterChips = ({ label, allLabel, options, value, onSelect }: FilterChipsProps) => {
  if (options.length < 2) return null;

  return (
    <div className={styles.chips} role="group" aria-label={label}>
      <Chip active={value === ""} onClick={() => onSelect("")}>
        {allLabel}
      </Chip>
      {options.map((option) => (
        <Chip
          key={option.value}
          active={value === option.value}
          onClick={() => onSelect(option.value)}
        >
          {option.label}
        </Chip>
      ))}
    </div>
  );
};

export default FilterChips;
