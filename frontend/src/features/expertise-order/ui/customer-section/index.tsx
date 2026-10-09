import type { CustomerType } from "@/entities/expertise";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import type { FormErrors } from "../../model/types";
import type { Order } from "../../model/use-order";
import FieldGroup from "../field-group";
import Segments from "../segments";
import {
  COMPANY_INPUTS,
  CUSTOMER_TYPES,
  ENTREPRENEUR_INPUTS,
  INDIVIDUAL_INPUTS,
} from "./inputs";
import styles from "./style.module.scss";

type CustomerSectionProps = {
  order: Order;
  errors: FormErrors;
  cardAccept?: string;
};

const DEFAULT_CARD_ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const NOTES: Record<CustomerType, string> = {
  legal:
    "Оплата по счёту. По реквизитам составим договор, счёт и акт. Заявки можно подавать от разных организаций — реквизиты указываются в каждой.",
  entrepreneur: "Оплата по счёту. По реквизитам ИП составим договор, счёт и акт.",
  individual: "Оплата картой. Паспортные данные нужны только для договора.",
};

const CustomerSection = ({
  order,
  errors,
  cardAccept = DEFAULT_CARD_ACCEPT,
}: CustomerSectionProps) => {
  const { state } = order;
  const individual = state.customerType === "individual";
  const companyInputs = state.customerType === "entrepreneur" ? ENTREPRENEUR_INPUTS : COMPANY_INPUTS;
  const types = CUSTOMER_TYPES.filter((item) => order.customerTypes.includes(item.value));

  return (
    <>
      <FieldGroup label="Заказчик">
        <Segments
          label="Кто заказчик"
          options={types}
          value={state.customerType}
          onChange={(value) => order.selectCustomerType(value as CustomerType)}
        />
        <p className={styles.note}>{NOTES[state.customerType]}</p>

        <div className={styles.fields}>
          {individual
            ? INDIVIDUAL_INPUTS.map((input) => (
                <div key={input.field} className={input.wide ? styles.wide : undefined}>
                  <TextField
                    label={input.label}
                    required
                    type={input.type ?? "text"}
                    placeholder={input.placeholder}
                    inputMode={input.numeric ? "numeric" : undefined}
                    maxLength={500}
                    invalid={Boolean(errors[`individual-${input.field}`])}
                    value={state.individual[input.field]}
                    onChange={(value) => order.changeIndividual(input.field, value)}
                  />
                </div>
              ))
            : companyInputs.map((input) => (
                <div key={input.field} className={input.wide ? styles.wide : undefined}>
                  <TextField
                    label={input.label}
                    required={!input.optional}
                    placeholder={input.placeholder}
                    inputMode={input.numeric ? "numeric" : undefined}
                    maxLength={500}
                    invalid={Boolean(errors[`company-${input.field}`])}
                    value={state.company[input.field]}
                    onChange={(value) => order.changeCompany(input.field, value)}
                  />
                </div>
              ))}
        </div>
      </FieldGroup>

      {!individual && (
        <FilesField
          label="Карточка организации"
          files={state.companyCard ? [state.companyCard] : []}
          accept={cardAccept}
          hint="Приложите карточку с реквизитами, чтобы бухгалтерия сверила данные."
          onAdd={order.setCard}
          onRemove={order.removeCard}
        />
      )}
    </>
  );
};

export default CustomerSection;
