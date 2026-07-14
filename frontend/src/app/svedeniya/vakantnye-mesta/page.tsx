import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaVakantnye from "@/widgets/svedeniya/vakantnye-mesta";

export const metadata: Metadata = {
  title:
    "Вакантные места для приема (перевода) обучающихся — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaVakantnyePage() {
  return (
    <SvedeniyaPage
      activeSlug="vakantnye-mesta"
      crumb="Вакантные места для приема (перевода) обучающихся"
    >
      <SvedeniyaVakantnye />
    </SvedeniyaPage>
  );
}
