import classNames from "classnames";
import styles from "./style.module.scss";

type SegmentOption = {
  value: string;
  label: string;
  title?: string;
};

type SegmentsProps = {
  label: string;
  options: SegmentOption[];
  value: string;
  onChange: (value: string) => void;
};

const Segments = ({ label, options, value, onChange }: SegmentsProps) => (
  <div className={styles.segments} role="tablist" aria-label={label}>
    {options.map((option) => (
      <button
        key={option.value}
        type="button"
        role="tab"
        aria-selected={option.value === value}
        title={option.title}
        className={classNames(styles.segment, option.value === value && styles.active)}
        onClick={() => onChange(option.value)}
      >
        {option.label}
      </button>
    ))}
  </div>
);

export type { SegmentOption };

export default Segments;
