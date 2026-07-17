import type { ReactNode } from "react";
import SectionHeading from "@/shared/ui/section-heading";
import { PRIVACY_POLICY, type PolicyBlock } from "./data";
import styles from "./style.module.scss";

const LINK_PATTERN = /\[([^\]]+)]\(([^)]+)\)/g;

const renderText = (text: string): ReactNode[] => {
  const parts: ReactNode[] = [];
  let cursor = 0;

  for (const match of text.matchAll(LINK_PATTERN)) {
    const index = match.index ?? 0;

    if (index > cursor) parts.push(text.slice(cursor, index));

    parts.push(
      <a className={styles.link} href={match[2]} key={`${match[2]}-${index}`}>
        {match[1]}
      </a>,
    );

    cursor = index + match[0].length;
  }

  if (cursor < text.length) parts.push(text.slice(cursor));

  return parts;
};

const PolicyBlockContent = ({ block }: { block: PolicyBlock }) => {
  if (block.type === "paragraph") {
    return <p>{renderText(block.text)}</p>;
  }

  if (block.type === "list") {
    return (
      <div className={styles.block}>
        <p>{block.intro}</p>
        <ul className={block.marker === "dash" ? styles.dashList : styles.list}>
          {block.items.map((item) => (
            <li key={item}>{renderText(item)}</li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <dl className={styles.details}>
      {block.items.map((item) => (
        <div className={styles.detail} key={item.label}>
          <dt>{item.label}</dt>
          <dd>
            {item.list ? (
              <ul className={styles.list}>
                {item.values.map((value) => (
                  <li key={value}>{renderText(value)}</li>
                ))}
              </ul>
            ) : (
              item.values.map((value) => <p key={value}>{renderText(value)}</p>)
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
};

const PrivacyPolicy = () => (
  <div className={styles.policy}>
    <SectionHeading title={PRIVACY_POLICY.title} />

    <div className={styles.content}>
      {PRIVACY_POLICY.sections.map((section) => (
        <section className={styles.section} key={section.number}>
          <div className={styles.sectionHeading}>
            <span className={styles.sectionNumber}>{section.number}</span>
            <h2 className={styles.sectionTitle}>{section.title}</h2>
          </div>

          {section.blocks.map((block, index) => (
            <PolicyBlockContent block={block} key={`${section.number}-${index}`} />
          ))}
        </section>
      ))}
    </div>
  </div>
);

export default PrivacyPolicy;
