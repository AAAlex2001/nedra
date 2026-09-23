"use client";

import { Fragment, useState } from "react";
import type { Direction } from "@/entities/service";
import DetailPanel from "../detail-panel";
import DirectionHeader from "../direction-header";
import ServicesModal from "../services-modal";
import Heading from "@/shared/ui/block-heading";
import styles from "./style.module.scss";

type CatalogProps = {
  directions: Direction[];
  heading: { title: string; subtitle: string };
};

const DESKTOP = "(min-width: 1440px)";

const Catalog = ({ directions, heading }: CatalogProps) => {
  const [activeId, setActiveId] = useState(directions[0].id);
  const [modalOpen, setModalOpen] = useState(false);

  const activeDirection =
    directions.find((direction) => direction.id === activeId) ?? directions[0];

  const select = (id: string) => {
    setActiveId(id);

    if (!window.matchMedia(DESKTOP).matches) setModalOpen(true);
  };

  return (
    <div className={styles.catalog}>
      <div className={styles.headingCell}>
        <Heading title={heading.title} subtitle={heading.subtitle} />
      </div>

      {directions.map((direction) => {
        const isOpen = direction.id === activeId;

        return (
          <Fragment key={direction.id}>
            <DirectionHeader
              direction={direction}
              isOpen={isOpen}
              onSelect={() => select(direction.id)}
            />
            {isOpen && (
              <div className={styles.drawer}>
                <DetailPanel key={direction.id} direction={direction} />
              </div>
            )}
          </Fragment>
        );
      })}

      <ServicesModal
        open={modalOpen}
        title={activeDirection.title}
        onClose={() => setModalOpen(false)}
      >
        <DetailPanel key={activeDirection.id} direction={activeDirection} />
      </ServicesModal>
    </div>
  );
};

export default Catalog;
