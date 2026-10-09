import type { HazardClass } from "@/entities/expert";
import type { RequirementMode } from "../../model/types";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";
import Segments from "../segments";

type RequirementSectionProps = {
  hazardClasses: HazardClass[];
  categories: number[];
  mode: RequirementMode;
  hazardClass: number | null;
  category: number | null;
  requiredCategory: number | null;
  onMode: (mode: RequirementMode) => void;
  onHazard: (value: number) => void;
  onCategory: (value: number) => void;
};

const MODES: { value: RequirementMode; label: string }[] = [
  { value: "hazard", label: "Класс опасности ОПО" },
  { value: "category", label: "Категория эксперта" },
  { value: "unknown", label: "Не знаю" },
];

const describe = (mode: RequirementMode, requiredCategory: number | null): string => {
  if (mode === "unknown") {
    return "Заявку увидят все аттестованные эксперты, подходящего подберём по документации.";
  }

  if (requiredCategory === null) {
    return "Класс опасности указан в свидетельстве о регистрации ОПО. По нему подберём категорию эксперта.";
  }

  return `Заявку увидят эксперты ${requiredCategory} категории и выше.`;
};

const toText = (value: number | null): string | null => {
  if (value === null) return null;

  return String(value);
};

const RequirementSection = ({
  hazardClasses,
  categories,
  mode,
  hazardClass,
  category,
  requiredCategory,
  onMode,
  onHazard,
  onCategory,
}: RequirementSectionProps) => {
  const hazardOptions = hazardClasses.map((rule) => ({
    value: String(rule.hazard_class),
    label: `${rule.hazard_class} класс`,
  }));

  const categoryOptions = categories.map((item) => ({
    value: String(item),
    label: `${item} категория`,
  }));

  return (
    <FieldGroup label="Требования к эксперту" note={describe(mode, requiredCategory)}>
      <Segments
        label="Как задать требование"
        options={MODES}
        value={mode}
        onChange={(value) => onMode(value as RequirementMode)}
      />

      {mode === "hazard" && (
        <ChipOptions
          label="Класс опасности"
          layout="row"
          options={hazardOptions}
          value={toText(hazardClass)}
          onChange={(value) => onHazard(Number(value))}
        />
      )}

      {mode === "category" && (
        <ChipOptions
          label="Категория эксперта"
          layout="row"
          options={categoryOptions}
          value={toText(category)}
          onChange={(value) => onCategory(Number(value))}
        />
      )}
    </FieldGroup>
  );
};

export default RequirementSection;
