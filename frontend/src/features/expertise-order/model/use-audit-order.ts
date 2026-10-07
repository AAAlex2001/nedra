"use client";

import { createAudit } from "@/entities/expertise";
import type { AuditFile } from "./types";
import { useOrder } from "./use-order";

export const useAuditOrder = () => {
  const order = useOrder();
  const { state, dispatch } = order;

  const canSubmit = order.ready && state.auditFiles.length > 0;

  const addFiles = (item: number, files: File[]) =>
    dispatch({ type: "auditFiles/add", item, files });
  const removeFile = (target: AuditFile) => dispatch({ type: "auditFiles/remove", target });

  const submit = async () => {
    if (!canSubmit) return;

    const formData = new FormData();
    formData.append("payload", JSON.stringify(order.payload));

    for (const entry of state.auditFiles) {
      formData.append("files", entry.file);
      formData.append("items", String(entry.item));
    }

    await order.send(formData, createAudit);
  };

  return { order, canSubmit, addFiles, removeFile, submit };
};
