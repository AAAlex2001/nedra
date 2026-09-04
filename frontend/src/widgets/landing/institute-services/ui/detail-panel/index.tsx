"use client";

import { useState } from "react";
import type { Direction } from "@/entities/service";
import HeroCard from "../hero-card";
import LicenseCard from "../license-card";
import ServiceDetails from "../service-details";
import ServiceTabs from "../service-tabs";
import styles from "./style.module.scss";

type DetailPanelProps = {
  direction: Direction;
};

const DetailPanel = ({ direction }: DetailPanelProps) => {
  const [activeServiceId, setActiveServiceId] = useState(direction.services[0].id);
  const activeService =
    direction.services.find((service) => service.id === activeServiceId) ??
    direction.services[0];
  const hasMultipleServices = direction.services.length > 1;

  const details = (
    <>
      <ServiceDetails service={activeService} />
      {activeService.licenses && <LicenseCard licenses={activeService.licenses} />}
    </>
  );

  return (
    <aside className={styles.panel} role="tabpanel">
      <HeroCard direction={direction} />

      {hasMultipleServices ? (
        <div className={styles.split}>
          <ServiceTabs
            services={direction.services}
            activeId={activeService.id}
            onSelect={setActiveServiceId}
          />
          <div className={styles.column}>{details}</div>
        </div>
      ) : (
        details
      )}
    </aside>
  );
};

export default DetailPanel;
