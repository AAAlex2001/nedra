import Image from "next/image";
import Link from "next/link";
import styles from "./style.module.scss";

const SERVICES = [
  {
    href: "/blits-ekspert",
    name: "Блиц-эксперт",
    caption: "Онлайн экспертиза",
    image: "/blitz/20.webp",
    tone: "expert",
    action: "Рассчитать",
  },
  {
    href: "/blits-audit",
    name: "Блиц-аудит",
    caption: "Аудит безопасности",
    image: "/audit/1.webp",
    tone: "audit",
    action: "Открыть",
  },
];

export default function GuestBar() {
  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />
      <aside className={styles.bar} aria-label="Онлайн-сервисы НПИ «Недра»">
        {SERVICES.map((service) => (
          <div key={service.href} className={`${styles.item} ${styles[service.tone]}`}>
            <Link href={service.href} className={styles.text}>
              <Image
                className={styles.artwork}
                src={service.image}
                alt=""
                width={52}
                height={52}
                sizes="52px"
              />
              <span className={styles.copy}>
                <span className={styles.title}>{service.name}</span>
                <span className={styles.caption}>{service.caption}</span>
              </span>
            </Link>
            <Link
              href={service.href}
              className={styles.pill}
              aria-label={`${service.action}: ${service.name}`}
            >
              {service.action}
            </Link>
          </div>
        ))}
      </aside>
    </>
  );
}
