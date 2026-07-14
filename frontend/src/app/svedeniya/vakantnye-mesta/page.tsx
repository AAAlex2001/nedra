import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaVakantnye from "@/widgets/svedeniya/vakantnye-mesta";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/vakantnye-mesta");

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
