"use client";

import type { AuditChecklistItem } from "@/entities/expertise";
import TextField from "@/shared/ui/text-field";
import { useAuditOrder } from "../../model/use-audit-order";
import AuditChecklist from "../audit-checklist";
import CustomerSection from "../customer-section";
import DeadlineSection from "../deadline-section";
import OrderShell from "../order-shell";
import PriceSection from "../price-section";

type AuditFormProps = {
  checklist: AuditChecklistItem[];
};

const AuditForm = ({ checklist }: AuditFormProps) => {
  const audit = useAuditOrder();
  const { order } = audit;
  const { state } = order;

  return (
    <OrderShell
      order={order}
      executors="Аудиторы"
      submitText="Отправить на аудит"
      canSubmit={audit.canSubmit}
      onSubmit={audit.submit}
    >
      <TextField
        label="Объект аудита"
        required
        placeholder="Организация или опасный производственный объект"
        maxLength={500}
        value={state.objectName}
        onChange={order.changeObjectName}
      />

      <DeadlineSection
        label="Когда нужен отчёт"
        executor="аудитора"
        value={state.deadline}
        onSelect={order.selectDeadline}
      />

      <PriceSection
        label="Ваша цена за аудит, ₽"
        executors="Аудиторы"
        value={state.price}
        onChange={order.changePrice}
      />

      <AuditChecklist
        checklist={checklist}
        files={state.auditFiles}
        onAdd={audit.addFiles}
        onRemove={audit.removeFile}
      />

      <CustomerSection order={order} />

      <TextField
        label="Комментарий"
        multiline
        placeholder="Что важно знать аудитору: структура организации, количество ОПО, на что обратить внимание"
        maxLength={4000}
        value={state.comment}
        onChange={order.changeComment}
      />
    </OrderShell>
  );
};

export default AuditForm;
