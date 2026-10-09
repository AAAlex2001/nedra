"use client";

import { useState } from "react";
import {
  invoicePdfUrl,
  issueInvoice,
  reportInvoicePaid,
  type PaymentDocumentKind,
} from "@/entities/billing";
import {
  acceptExpertise,
  acceptWork,
  answerAuditCounter,
  answerAuditOffer,
  approveAuditPlan,
  confirmExpertise,
  createExpertisePayment,
  markConclusionReady,
  proposeAuditPrice,
  refreshExpertisePayment,
  requestAuditPlanChanges,
  resubmitDocumentation,
  sendAuditPlan,
  sendConclusion,
  sendRemarks,
  setAuditTeam,
  uploadAuditDocuments,
  type AuditFile,
  type AuditPlanInput,
  type ContractKind,
  type Expertise,
  type OfferAnswer,
} from "@/entities/expertise";

const ACTION_FAILED = "Не удалось выполнить действие. Попробуйте ещё раз.";

export const useExpertiseActions = (expertise: Expertise, onChange: (item: Expertise) => void) => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<Expertise>): Promise<boolean> => {
    setPending(true);
    setError(null);

    try {
      const updated = await action();
      onChange(updated);
      return true;
    } catch (caught) {
      const message = caught instanceof Error && caught.message ? caught.message : ACTION_FAILED;
      setError(message);
      return false;
    } finally {
      setPending(false);
    }
  };

  const accept = (contractKind: ContractKind | null) =>
    run(() => acceptExpertise(expertise.id, contractKind));
  const confirm = () => run(() => confirmExpertise(expertise.id));
  const conclusionReady = () => run(() => markConclusionReady(expertise.id));
  const finish = () => run(() => acceptWork(expertise.id));
  const refresh = () => run(() => refreshExpertisePayment(expertise.id));
  const submitConclusion = (formData: FormData) =>
    run(() => sendConclusion(expertise.id, formData));
  const submitRemarks = (formData: FormData) => run(() => sendRemarks(expertise.id, formData));
  const submitRevision = (formData: FormData) =>
    run(() => resubmitDocumentation(expertise.id, formData));
  const proposePrice = (price: number) => run(() => proposeAuditPrice(expertise.id, price));
  const answerOffer = (answer: OfferAnswer, price?: number) =>
    run(() => answerAuditOffer(expertise.id, answer, price ?? null));
  const answerCounter = (accept: boolean) => run(() => answerAuditCounter(expertise.id, accept));
  const saveTeam = (userIds: number[]) => run(() => setAuditTeam(expertise.id, userIds));
  const sendPlan = (plan: AuditPlanInput) => run(() => sendAuditPlan(expertise.id, plan));
  const approvePlan = () => run(() => approveAuditPlan(expertise.id));
  const requestPlanChanges = (comment: string) =>
    run(() => requestAuditPlanChanges(expertise.id, comment));
  const uploadDocuments = (files: AuditFile[]) =>
    run(() => uploadAuditDocuments(expertise.id, files));

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

  const reportPaid = async (
    document: File | null = null,
    documentKind: PaymentDocumentKind = "payment_order",
  ) => {
    const invoice = expertise.invoice;

    if (invoice === null) return;

    setPending(true);
    setError(null);

    try {
      const updated = await reportInvoicePaid(invoice.id, document, documentKind);
      onChange({ ...expertise, invoice: { ...invoice, reported_at: updated.reported_at } });
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
    reportPaid,
    refresh,
    conclusionReady,
    submitConclusion,
    submitRemarks,
    submitRevision,
    finish,
    proposePrice,
    answerOffer,
    answerCounter,
    saveTeam,
    sendPlan,
    approvePlan,
    requestPlanChanges,
    uploadDocuments,
  };
};

export type ExpertiseActionsState = ReturnType<typeof useExpertiseActions>;
