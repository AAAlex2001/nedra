import RadioButton from "@/shared/ui/radio-button";
import type { SubService } from "@/entities/service";
import styles from "./style.module.scss";

type ServiceTabsProps = {
  services: SubService[];
  activeId: string;
  onSelect: (id: string) => void;
};

const ServiceTabs = ({ services, activeId, onSelect }: ServiceTabsProps) => (
  <div className={styles.tabs} role="radiogroup" aria-label="Услуги направления">
    {services.map((service) => (
      <RadioButton
        key={service.id}
        checked={service.id === activeId}
        label={service.label}
        onSelect={() => onSelect(service.id)}
      />
    ))}
  </div>
);

export default ServiceTabs;
