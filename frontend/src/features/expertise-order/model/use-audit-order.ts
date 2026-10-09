"use client";

import { useState } from "react";
import { createAudit, type AuditFile, type CustomerType } from "@/entities/expertise";
import { useSession } from "@/entities/user";
import { emptyAuditForm, toAuditDetails, type AuditForm } from "./audit-form";
import { auditErrors } from "./audit-validation";
import { useOrder } from "./use-order";

export const AUDIT_CUSTOMER_TYPES: CustomerType[] = ["legal", "entrepreneur"];

export const useAuditOrder = () => {
  const { user } = useSession();
  const order = useOrder(AUDIT_CUSTOMER_TYPES);

  const newForm = () => emptyAuditForm(user?.full_name ?? "", user?.phone ?? "", user?.email ?? "");
  const [form, setForm] = useState<AuditForm>(newForm);

  const allErrors = { ...auditErrors(form, order.price), ...order.customerProblems };
  const hasErrors = Object.keys(allErrors).length > 0;
  const errors = order.attempted ? allErrors : {};

  const changeForm = (next: AuditForm) => {
    const organization = next.applicant.organization;
    const inn = next.applicant.inn;

    setForm(next);

    if (organization !== form.applicant.organization) order.changeCompany("name", organization);
    if (inn !== form.applicant.inn) order.changeCompany("inn", inn);
  };

  const addFiles = (item: number, files: File[]) =>
    order.dispatch({ type: "auditFiles/add", item, files });

  const removeFile = (target: AuditFile) => order.dispatch({ type: "auditFiles/remove", target });

  const submit = async () => {
    order.markAttempted();
    if (hasErrors) return;

    const payload = {
      customer_type: order.payload.customer_type,
      company: order.payload.company,
      comment: order.payload.comment,
      price: form.budget === "custom" ? order.price : null,
      details: toAuditDetails(form),
    };

    const formData = new FormData();
    formData.append("payload", JSON.stringify(payload));

    for (const entry of order.state.auditFiles) {
      formData.append("files", entry.file);
      formData.append("items", String(entry.item));
    }

    if (form.scope === "all" && form.certificate) formData.append("opo_certificate", form.certificate);
    if (form.applicant.by_proxy && form.proxyFile) formData.append("power_of_attorney", form.proxyFile);
    if (form.useSto && form.stoFile) formData.append("sto_file", form.stoFile);

    const sent = await order.send(formData, createAudit);

    if (sent) setForm(newForm());
  };

  return { order, form, errors, changeForm, addFiles, removeFile, submit };
};
