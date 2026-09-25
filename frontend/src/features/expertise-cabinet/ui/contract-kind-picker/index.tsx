import { CONTRACT_KIND_LABELS, type ContractKind } from "@/entities/expertise";
import Chip from "@/shared/ui/chip";
import styles from "./style.module.scss";

type ContractKindPickerProps = {
  kinds: ContractKind[];
  value: ContractKind | null;
  onChange: (kind: ContractKind) => void;
};

const ContractKindPicker = ({ kinds, value, onChange }: ContractKindPickerProps) => (
  <div className={styles.picker} role="group" aria-label="Вид договора">
    {kinds.map((kind) => (
      <Chip key={kind} active={value === kind} onClick={() => onChange(kind)}>
        {CONTRACT_KIND_LABELS[kind]}
      </Chip>
    ))}
  </div>
);

export default ContractKindPicker;
