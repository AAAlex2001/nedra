import type { ReactNode } from "react";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import type { LegalBlock, LegalDocument, LegalSection } from "./types";
import styles from "./style.module.scss";

export { PRIVACY_POLICY } from "./data/privacy";
export { PUBLIC_OFFER } from "./data/offer";
export { USER_AGREEMENT } from "./data/agreement";
export { PERSONAL_DATA_CONSENT } from "./data/consent";

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

const LegalBlockContent = ({ block }: { block: LegalBlock }) => {
  if (block.type === "paragraph") {
    return <p>{renderText(block.text)}</p>;
  }

  if (block.type === "list") {
    return (
      <div className={styles.block}>
        <p>{renderText(block.intro)}</p>
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

const SectionBlocks = ({ section }: { section: LegalSection }) =>
  section.blocks.map((block, index) => (
    <LegalBlockContent block={block} key={`${section.number}-${index}`} />
  ));

const LegalSectionContent = ({ section }: { section: LegalSection }) => {
  if (!section.title) {
    return (
      <section className={styles.numbered}>
        <span className={styles.itemNumber}>{section.number}</span>
        <div className={styles.section}>
          <SectionBlocks section={section} />
        </div>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <div className={styles.sectionHeading}>
        <span className={styles.sectionNumber}>{section.number}</span>
        <h2 className={styles.sectionTitle}>{section.title}</h2>
      </div>

      <SectionBlocks section={section} />
    </section>
  );
};

const LegalDocumentView =({ document }: { document: LegalDocument }) => (
  <div className={styles.policy}>
    <SectionHeading title={document.title} />

    <div className={styles.content}>
      {document.intro && (
        <div className={styles.section}>
          {document.intro.map((text) => (
            <p key={text}>{renderText(text)}</p>
          ))}
        </div>
      )}

      {document.sections.map((section) => (
        <LegalSectionContent section={section} key={section.number} />
      ))}
    </div>
  </div>
);

type LegalPageProps = {
  document: LegalDocument;
  label: string;
};

const LegalPage = ({ document, label }: LegalPageProps) => (
  <main className={styles.page}>
    <Breadcrumbs
      items={[
        { label: "Главная", href: "/" },
        { label },
      ]}
    />

    <div className={styles.body}>
      <LegalDocumentView document={document} />
    </div>
  </main>
);

export default LegalPage;
