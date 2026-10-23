import Image from "next/image";
import Link from "next/link";
import styles from "./style.module.scss";

const SERVICES = [
  { href: "/blits-ekspert", name: "Блиц-эксперт", caption: "Онлайн экспертиза", image: "/blitz/20.webp", tone: "expert" },
  { href: "/blits-audit", name: "Блиц-аудит", caption: "Аудит безопасности", image: "/audit/1.webp", tone: "audit" },
];

export default function ServiceNavigation({ compact = false, onNavigate }: { compact?: boolean; onNavigate?: () => void }) {
  return (
    <div className={compact ? styles.promo : styles.services}>
      {SERVICES.map((service) => (
        <Link key={service.href} href={service.href} onClick={onNavigate} className={`${styles.service} ${styles[service.tone]}`}>
          <Image className={styles.artwork} src={service.image} alt="" width={120} height={120} sizes={compact ? "40px" : "84px"} />
          <span className={styles.name}>{service.name}</span>
          {!compact && <span className={styles.caption}>{service.caption}</span>}
        </Link>
      ))}
    </div>
  );
}
