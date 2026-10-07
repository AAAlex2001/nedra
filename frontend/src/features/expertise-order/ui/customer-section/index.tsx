import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import type { Order } from "../../model/use-order";
import FieldGroup from "../field-group";
import Segments from "../segments";
import { COMPANY_INPUTS, CUSTOMER_TYPES, INDIVIDUAL_INPUTS } from "./inputs";
import styles from "./style.module.scss";

type CustomerSectionProps = {
  order: Order;
};

const CARD_ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const LEGAL_NOTE =
  "Оплата по счёту. По реквизитам составим договор, счёт и акт. Заявки можно подавать от разных организаций — реквизиты указываются в каждой.";

const INDIVIDUAL_NOTE = "Оплата картой. Паспортные данные нужны только для договора.";

const CustomerSection = ({ order }: CustomerSectionProps) => {
  const { state } = order;
  const legal = state.customerType === "legal";

  return (
    <>
      <FieldGroup label="Заказчик">
        <Segments
          label="Кто заказчик"
          options={CUSTOMER_TYPES}
          value={state.customerType}
          onChange={order.selectCustomerType}
        />
        <p className={styles.note}>{legal ? LEGAL_NOTE : INDIVIDUAL_NOTE}</p>

        <div className={styles.fields}>
          {legal
            ? COMPANY_INPUTS.map((input) => (
                <div key={input.field} className={input.wide ? styles.wide : undefined}>
                  <TextField
                    label={input.label}
                    required={!input.optional}
                    placeholder={input.placeholder}
                    inputMode={input.numeric ? "numeric" : undefined}
                    maxLength={500}
                    value={state.company[input.field]}
                    onChange={(value) => order.changeCompany(input.field, value)}
                  />
                </div>
              ))
            : INDIVIDUAL_INPUTS.map((input) => (
                <div key={input.field} className={input.wide ? styles.wide : undefined}>
                  <TextField
                    label={input.label}
                    required
                    type={input.type ?? "text"}
                    placeholder={input.placeholder}
                    inputMode={input.numeric ? "numeric" : undefined}
                    maxLength={500}
                    value={state.individual[input.field]}
                    onChange={(value) => order.changeIndividual(input.field, value)}
                  />
                </div>
              ))}
        </div>
      </FieldGroup>

      {legal && (
        <FilesField
          label="Карточка организации"
          files={state.companyCard ? [state.companyCard] : []}
          accept={CARD_ACCEPT}
          hint="Приложите карточку с реквизитами, чтобы бухгалтерия сверила данные."
          onAdd={order.setCard}
          onRemove={order.removeCard}
        />
      )}
    </>
  );
};

export default CustomerSection;
