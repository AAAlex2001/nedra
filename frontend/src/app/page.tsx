import Activities from "@/widgets/landing/activities";
import Advantages from "@/widgets/landing/advantages";
import Directions from "@/widgets/landing/directions";
import Documents from "@/widgets/landing/documents";
import Fields from "@/widgets/landing/fields";
import Heritage from "@/widgets/landing/heritage";
import Hero from "@/widgets/landing/hero";
import Institute from "@/widgets/landing/institute";
import Laboratory from "@/widgets/landing/laboratory";
import Partners from "@/widgets/landing/partners";
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
      <Heritage />
      <Institute />
      <Documents />
      <Advantages />
      <Partners />
    </main>
  );
}
