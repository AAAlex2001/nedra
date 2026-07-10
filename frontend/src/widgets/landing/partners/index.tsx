"use client";

import Marquee from "react-fast-marquee";
import AccentLine from "@/shared/ui/accent-line";
import { LAST_ROW, PARTNERS_DATA, ROWS, type Logo } from "./data";
import styles from "./style.module.scss";

const MARQUEE_ROWS: Logo[][] = [
  ROWS[0],
  [...ROWS[1], LAST_ROW[0]],
  ROWS[2],
  [...ROWS[3], LAST_ROW[1]],
];

const LogoCell = ({ item }: { item: Logo }) => {
  if (item.kind === "svg") {
    const { Logo: LogoComponent } = item;
    return <LogoComponent className={styles.logo} />;
  }

  if (item.kind === "img") {
    return (
      <img
        className={styles.logo}
        src={item.src}
        alt={item.label}
        loading="lazy"
        draggable={false}
      />
    );
  }

  return (
    <span
      className={styles.placeholder}
      style={{ width: item.width, height: item.height }}
      title={`Нет логотипа: ${item.label}`}
    >
      {item.label}
    </span>
  );
};

const Partners = () => {
  return (
    <section className={styles.section}>
      <div className={styles.heading}>
        <h2 className={styles.title}>{PARTNERS_DATA.title}</h2>
        <AccentLine width={30} />
        <p className={styles.subtitle}>{PARTNERS_DATA.subtitle}</p>
      </div>

      <div className={styles.grid}>
        {MARQUEE_ROWS.map((row, index) => (
          <Marquee
            key={index}
            className={styles.marquee}
            direction={index % 2 === 0 ? "left" : "right"}
            speed={40}
            autoFill
            pauseOnHover
            gradient
            gradientColor="#FFFFFF"
            gradientWidth={120}
          >
            {row.map((item) => (
              <a
                key={item.label}
                className={styles.cell}
                href={item.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={item.label}
              >
                <LogoCell item={item} />
              </a>
            ))}
          </Marquee>
        ))}
      </div>

      <p className={styles.note}>{PARTNERS_DATA.note}</p>
    </section>
  );
};

export default Partners;
