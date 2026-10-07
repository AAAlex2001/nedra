import {
  CheckIcon,
  ClockIcon,
  DirectorIcon,
  DocumentIcon,
  PeopleIcon,
  ProcedureDocumentIcon,
} from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type LandingIcon = "document" | "clock" | "check" | "people" | "certificate" | "shield";

export type LandingFeature = {
  title: string;
  text: string;
  icon: LandingIcon;
};

type LandingFeaturesProps = {
  title: string;
  items: LandingFeature[];
};

const ICONS = {
  document: DocumentIcon,
  clock: ClockIcon,
  check: CheckIcon,
  people: PeopleIcon,
  certificate: DirectorIcon,
  shield: ProcedureDocumentIcon,
};

const LandingFeatures = ({ title, items }: LandingFeaturesProps) => (
  <section className={styles.features}>
    <h2 className={styles.title}>{title}</h2>

    <div className={styles.grid}>
      {items.map((card) => {
        const Icon = ICONS[card.icon];

        return (
          <article key={card.title} className={styles.card}>
            <span className={styles.tile} aria-hidden="true">
              <Icon className={styles.icon} />
            </span>
            <h3 className={styles.cardTitle}>{card.title}</h3>
            <p className={styles.cardText}>{card.text}</p>
          </article>
        );
      })}
    </div>
  </section>
);

export default LandingFeatures;
