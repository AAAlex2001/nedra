"use client";

import { useState } from "react";
import { invoicePdfUrl, issueInvoice } from "@/entities/billing";
import {
  acceptExpertise,
  acceptWork,
  confirmExpertise,
  createExpertisePayment,
  markConclusionReady,
  refreshExpertisePayment,
  resubmitDocumentation,
  sendConclusion,
  sendRemarks,
  type Expertise,
} from "@/entities/expertise";

const ACTION_FAILED = "Не удалось выполнить действие. Попробуйте ещё раз.";

export const useExpertiseActions = (expertise: Expertise, onChange: (item: Expertise) => void) => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<Expertise>) => {
    setPending(true);
    setError(null);

    try {
      const updated = await action();
      onChange(updated);
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
    } finally {
      setPending(false);
    }
  };

  const accept = () => run(() => acceptExpertise(expertise.id));
  const confirm = () => run(() => confirmExpertise(expertise.id));
  const conclusionReady = () => run(() => markConclusionReady(expertise.id));
  const finish = () => run(() => acceptWork(expertise.id));
  const refresh = () => run(() => refreshExpertisePayment(expertise.id));
  const submitConclusion = (formData: FormData) =>
    run(() => sendConclusion(expertise.id, formData));
  const submitRemarks = (formData: FormData) => run(() => sendRemarks(expertise.id, formData));
  const submitRevision = (formData: FormData) =>
    run(() => resubmitDocumentation(expertise.id, formData));

  const requestInvoice = async () => {
    setPending(true);
    setError(null);

    try {
      const invoice = await issueInvoice(expertise.id);
      window.open(invoicePdfUrl(invoice.id), "_blank", "noreferrer");
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
    } finally {
      setPending(false);
    }
  };

  const pay = async () => {
    setPending(true);
    setError(null);

    try {
      const payment = await createExpertisePayment(expertise.id);

      if (payment.confirmation_url) {
        window.location.assign(payment.confirmation_url);
        return;
      }

      const updated = await refreshExpertisePayment(expertise.id);
      onChange(updated);
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
    } finally {
      setPending(false);
    }
  };

  return {
    pending,
    error,
    accept,
    confirm,
    pay,
    requestInvoice,
    refresh,
    conclusionReady,
    submitConclusion,
    submitRemarks,
    submitRevision,
    finish,
  };
};
