import Image from "next/image";
import type { Direction } from "@/entities/service";
import LicenseCard from "@/widgets/landing/institute-services/ui/license-card";
import ServiceDetails from "@/widgets/landing/institute-services/ui/service-details";
import ServiceSlider from "../service-slider";
import { SERVICE_PAGE_DETAILS } from "../../service-page-details";
import styles from "../../style.module.scss";

type DirectionSectionProps = {
  direction: Direction;
};

const DirectionSection = ({ direction }: DirectionSectionProps) => (
  <section className={styles.direction} aria-labelledby={`direction-${direction.id}`}>
    <div className={styles.overview}>
      <div className={styles.introduction}>
        <h2 id={`direction-${direction.id}`}>{direction.title}</h2>
        <p>{direction.summary}</p>
      </div>
      <div className={styles.picture}>
        <Image
          src={direction.image}
          alt={direction.title}
          fill
          sizes="(min-width: 1440px) 440px, (min-width: 768px) 340px, 100vw"
        />
      </div>
    </div>

    <ServiceSlider count={direction.services.length} title={direction.title}>
      {direction.services.map(service => (
        <article key={service.id} id={`service-${service.id}`} className={styles.service}>
          <h3>{service.label}</h3>
          <ServiceDetails
            service={service}
            sections={[
              {
                title: "Когда обращаться",
                text: SERVICE_PAGE_DETAILS[service.id].whenToContact,
              },
              ...service.sections,
              {
                title: "Что подготовить для обсуждения задачи",
                text: SERVICE_PAGE_DETAILS[service.id].documentsToPrepare,
              },
            ]}
          />
          {service.licenses && (
            <div className={styles.licenses}>
              <LicenseCard licenses={service.licenses} />
            </div>
          )}
        </article>
      ))}
    </ServiceSlider>
  </section>
);

export default DirectionSection;
