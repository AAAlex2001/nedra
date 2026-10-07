import type { ExpertiseObject } from "@/entities/expert";
import FieldGroup from "../field-group";
import Segments from "../segments";

type ObjectSectionProps = {
  objects: ExpertiseObject[];
  value: string;
  onSelect: (code: string) => void;
};

const UNKNOWN_NOTE = "Ничего страшного: эксперт определит объект по вашей документации.";

const ObjectSection = ({ objects, value, onSelect }: ObjectSectionProps) => {
  const current = objects.find((object) => object.code === value);

  const options = [
    ...objects.map((object) => ({ value: object.code, label: object.label, title: object.title })),
    { value: "", label: "Не знаю", title: "Эксперт определит по документации" },
  ];

  return (
    <FieldGroup label="Что проверяем" note={current ? current.title : UNKNOWN_NOTE}>
      <Segments label="Объект экспертизы" options={options} value={value} onChange={onSelect} />
    </FieldGroup>
  );
};

export default ObjectSection;
