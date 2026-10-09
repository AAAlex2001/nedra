"use client";

import classNames from "classnames";
import { useState } from "react";
import { invoicePdfUrl, type PaymentDocumentKind } from "@/entities/billing";
import {
  cardPaymentAllowed,
  contractKindsFor,
  isAudit,
  statusLabel,
  wordingFor,
  type ContractKind,
  type Expertise,
} from "@/entities/expertise";
import { useSession } from "@/entities/user";
import { formatRub, halfOf } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import { CheckIcon, ClockIcon } from "@/shared/ui/icons";
import { useExpertiseActions } from "../../model/use-expertise-actions";
import ConclusionForm from "../conclusion-form";
import ContractConsent from "../contract-consent";
import ContractKindPicker from "../contract-kind-picker";
import PaymentProofForm from "../payment-proof-form";
import RemarksForm from "../remarks-form";
import RevisionForm from "../revision-form";
import { auditCustomerStep, auditExpertStep } from "./audit-steps";
import { when, type Step } from "./step";
import styles from "./style.module.scss";

type ExpertiseActionsProps = {
  expertise: Expertise;
  role: "customer" | "expert";
  onChange: (item: Expertise) => void;
};

const PROOF_BUTTONS: { kind: PaymentDocumentKind; label: string }[] = [
  { kind: "payment_order", label: "Я оплатил" },
  { kind: "guarantee_letter", label: "Гарантийное письмо" },
];

const ExpertiseActions = ({ expertise, role, onChange }: ExpertiseActionsProps) => {
  const actions = useExpertiseActions(expertise, onChange);
  const { user } = useSession();
  const [remarksOpen, setRemarksOpen] = useState(false);
  const [proofKind, setProofKind] = useState<PaymentDocumentKind | null>(null);
  const [sentKind, setSentKind] = useState<PaymentDocumentKind | null>(null);
  const [contractKind, setContractKind] = useState<ContractKind | null>(expertise.contract_kind);

  const half = formatRub(halfOf(expertise.price));
  const price = formatRub(expertise.price);
  const invoice = expertise.invoice;
  const canReport = invoice !== null && invoice.reported_at === null;
  const guaranteed =
    sentKind === "guarantee_letter" ||
    expertise.documents.some((item) => item.kind === "guarantee_letter");
  const cardAllowed = cardPaymentAllowed(expertise);
  const kindUnknown = expertise.contract_kind === null;
  const audit = isAudit(expertise);
  const words = wordingFor(expertise);
  const lead = user !== null && expertise.expert_id === user.id;
  const executorName = expertise.expert_name ?? `${words.executor} НПИ «Недра»`;

  const toggleProof = (kind: PaymentDocumentKind) =>
    setProofKind(proofKind === kind ? null : kind);

  const payment = (hasPayment: boolean) => (
    <div className={styles.payment}>
      <div className={styles.payButtons}>
        {cardAllowed && (
          <Button
            className={styles.payCard}
            loading={actions.pending}
            onClick={() => void actions.pay()}
          >
            Оплатить картой {half}
          </Button>
        )}

        {!cardAllowed && invoice === null && (
          <Button
            className={styles.payCard}
            loading={actions.pending}
            onClick={() => void actions.requestInvoice()}
          >
            Получить счёт на {half}
          </Button>
        )}

        {!cardAllowed && invoice !== null && (
          <a
            className={styles.secondary}
            href={invoicePdfUrl(invoice.id)}
            target="_blank"
            rel="noreferrer"
          >
            Счёт № {invoice.number}
          </a>
        )}

        {canReport &&
          PROOF_BUTTONS.map((item) => (
            <button
              key={item.kind}
              type="button"
              className={classNames(styles.secondary, proofKind === item.kind && styles.secondaryActive)}
              disabled={actions.pending}
              onClick={() => toggleProof(item.kind)}
            >
              {item.label}
            </button>
          ))}

        {hasPayment && (
          <button
            type="button"
            className={styles.secondary}
            disabled={actions.pending}
            onClick={() => void actions.refresh()}
          >
            Проверить оплату
          </button>
        )}
      </div>

      {canReport && proofKind !== null && (
        <div className={styles.proof}>
          <PaymentProofForm
            key={proofKind}
            kind={proofKind}
            pending={actions.pending}
            onSubmit={(document) => {
              setProofKind(null);
              setSentKind(proofKind);
              void actions.reportPaid(document, proofKind);
            }}
          />
        </div>
      )}
    </div>
  );

  const customerStep = (): Step => {
    switch (expertise.status) {
      case "new":
        return {
          text: audit
            ? "Ждём, когда аудитор возьмёт заявку"
            : "Ждём, когда эксперт по вашей области возьмёт заявку",
        };

      case "expert_ready":
        return {
          text: `${executorName} готов провести ${words.work} за ${price}, оплата двумя частями по 50 %. Прочитайте договор и соглашение о конфиденциальности и подпишите их`,
          form: (
            <ContractConsent
              expertiseId={expertise.id}
              pending={actions.pending}
              onSign={() => void actions.confirm()}
            />
          ),
        };

      case "contract":
        return {
          text: cardAllowed
            ? `Договор заключён ${when(expertise.contract_at)}. Оплатите аванс картой, и ${words.executorLower} приступит к работе`
            : `Договор заключён ${when(expertise.contract_at)}. Оплатите аванс по счёту и приложите платёжное поручение или гарантийное письмо`,
          form: payment(expertise.advance_payment !== null),
        };

      case "in_progress":
        return {
          text: audit
            ? `Аванс оплачен ${when(expertise.advance_paid_at)}. Аудитор проверяет документы`
            : `Аванс оплачен ${when(expertise.advance_paid_at)}. Эксперт работает над заключением`,
        };

      case "remarks":
        return {
          text: audit
            ? "Аудитор прислал замечания. Дополните или исправьте документы и отправьте их повторно"
            : "Эксперт прислал замечания. Внесите изменения в документацию и отправьте её повторно",
          form: (
            <RevisionForm audit={audit} pending={actions.pending} onSubmit={actions.submitRevision} />
          ),
        };

      case "conclusion_ready":
        return {
          text: audit
            ? "Отчёт об аудите готов. Требуется полная оплата: внесите остаток, и аудитор отправит подписанный отчёт"
            : "Замечаний нет, заключение готово. Требуется полная оплата: внесите остаток, и эксперт отправит подписанный документ",
          form: payment(expertise.final_payment !== null),
        };

      case "paid":
        return {
          text: `Остаток оплачен ${when(expertise.final_paid_at)}. ${words.executor} подписывает ${words.resultLower} ЭЦП`,
        };

      case "sent":
        return {
          text: `${words.resultSent} ${when(expertise.sent_at)}. Скачайте файлы и примите работу`,
          action: (
            <Button loading={actions.pending} onClick={() => void actions.finish()}>
              Работа принята
            </Button>
          ),
        };

      case "accepted":
        return { text: `Работа принята ${when(expertise.accepted_at)}` };

      default:
        return { text: statusLabel(expertise) };
    }
  };

  const expertStep = (): Step => {
    switch (expertise.status) {
      case "new":
        return {
          text: kindUnknown
            ? `Заказчик предлагает ${price}. Он не знает вид проекта: определите его по документации. Нажимая «Готов провести», вы соглашаетесь с ценой`
            : `Заказчик предлагает ${price}. Нажимая «Готов провести», вы соглашаетесь с ценой. Заявку получит первый, кто подтвердит готовность`,
          action: (
            <Button
              disabled={contractKind === null}
              loading={actions.pending}
              onClick={() => void actions.accept(contractKind)}
            >
              Готов провести {words.work}
            </Button>
          ),
          form: kindUnknown ? (
            <ContractKindPicker
              kinds={contractKindsFor(expertise.object_code)}
              value={contractKind}
              onChange={setContractKind}
            />
          ) : null,
        };

      case "expert_ready":
        return { text: `Вы подтвердили готовность ${when(expertise.expert_ready_at)}. Ждём согласия заказчика` };

      case "contract":
        return { text: `Договор заключён ${when(expertise.contract_at)}. Ждём аванс от заказчика` };

      case "in_progress":
        return {
          text: audit
            ? "Документы у вас. Когда отчёт об аудите будет готов, отметьте это. Если документов не хватает или есть замечания, напишите заказчику"
            : "Документация у вас. Если замечаний нет, отметьте, что заключение готово, иначе пришлите рекомендации по приведению объекта в соответствие",
          action: remarksOpen ? null : (
            <>
              <button
                type="button"
                className={styles.secondary}
                disabled={actions.pending}
                onClick={() => setRemarksOpen(true)}
              >
                Есть замечания
              </button>
              <Button loading={actions.pending} onClick={() => void actions.conclusionReady()}>
                {words.resultReady}
              </Button>
            </>
          ),
          form: remarksOpen ? (
            <RemarksForm
              pending={actions.pending}
              onSubmit={actions.submitRemarks}
              onCancel={() => setRemarksOpen(false)}
            />
          ) : null,
        };

      case "remarks":
        return { text: "Замечания отправлены. Ждём исправленную документацию от заказчика" };

      case "conclusion_ready":
        return { text: "Ждём оплату остатка от заказчика" };

      case "paid":
        return {
          text: audit
            ? `Остаток оплачен ${when(expertise.final_paid_at)}. Приложите подписанный отчёт об аудите`
            : `Остаток оплачен ${when(expertise.final_paid_at)}. Приложите подписанное заключение`,
          form: (
            <ConclusionForm
              audit={audit}
              pending={actions.pending}
              onSubmit={actions.submitConclusion}
            />
          ),
        };

      case "sent":
        return { text: `${words.resultSent} ${when(expertise.sent_at)}. Ждём приёмки` };

      case "accepted":
        return { text: `Работа принята ${when(expertise.accepted_at)}` };

      default:
        return { text: statusLabel(expertise) };
    }
  };

  const auditStep = (): Step | null => {
    if (!audit) return null;

    return role === "customer"
      ? auditCustomerStep(expertise, actions)
      : auditExpertStep(expertise, actions, lead);
  };

  const ownStep = (): Step => (role === "customer" ? customerStep() : expertStep());
  const step = auditStep() ?? ownStep();
  const finished = expertise.status === "accepted";
  const waiting = !step.action && !step.form && !finished;

  return (
    <div className={styles.footer}>
      <div className={styles.row}>
        <p className={classNames(styles.text, finished && styles.textDone)}>
          {waiting && <ClockIcon className={styles.icon} />}
          {finished && <CheckIcon className={styles.icon} />}
          {step.text}
        </p>

        {step.action && <div className={styles.buttons}>{step.action}</div>}
      </div>

      {step.form}

      {role === "customer" && invoice !== null && invoice.reported_at !== null && (
        <p className={styles.note}>
          {guaranteed
            ? `Вы отправили гарантийное письмо по счёту № ${invoice.number} ${when(invoice.reported_at)}. Администратор рассмотрит его и подтвердит`
            : `Вы сообщили об оплате счёта № ${invoice.number} ${when(invoice.reported_at)}. Администратор проверит поступление на расчётный счёт и подтвердит оплату`}
        </p>
      )}

      {actions.error && <p className={styles.error}>{actions.error}</p>}
    </div>
  );
};

export default ExpertiseActions;
