import Activities from "@/widgets/landing/activities";
import Directions from "@/widgets/landing/directions";
import Fields from "@/widgets/landing/fields";
import Hero from "@/widgets/landing/hero";
import Laboratory from "@/widgets/landing/laboratory";
import Quality from "@/widgets/landing/quality";
import Services from "@/widgets/landing/services";

export default function Home() {
  return (
    <main>
      <Hero />
      <Directions />
      <Services />
      <Fields />
      <Quality />
      <Laboratory />
      <Activities />
    </main>
  );
}
