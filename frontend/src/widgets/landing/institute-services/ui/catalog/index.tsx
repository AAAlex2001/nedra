"use client";

import { Fragment, useState } from "react";
import type { Direction } from "@/entities/service";
import DetailPanel from "../detail-panel";
import DirectionHeader from "../direction-header";
import Heading from "../heading";
import styles from "./style.module.scss";

type CatalogProps = {
  directions: Direction[];
  heading: { title: string; subtitle: string };
};

const Catalog = ({ directions, heading }: CatalogProps) => {
  const [activeId, setActiveId] = useState(directions[0].id);

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
              onSelect={() => setActiveId(direction.id)}
            />
            {isOpen && (
              <div className={styles.drawer}>
                <DetailPanel key={direction.id} direction={direction} />
              </div>
            )}
          </Fragment>
        );
      })}
    </div>
  );
};

export default Catalog;
