"use client";

import { useCommissionPopup } from "../../model/popup-context";
import CommissionOffer from "../commission-offer";

const OfferBlock = () => {
  const { openForm } = useCommissionPopup();

  return <CommissionOffer onApply={openForm} />;
};

export default OfferBlock;
