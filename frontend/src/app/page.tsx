import Directions from "@/widgets/landing/directions";
import Activities from "@/widgets/landing/activities";
import Hero from "@/widgets/landing/hero";
import Advantages from "@/widgets/landing/advantages";
import Contacts from "@/widgets/landing/contacts";
import Documents from "@/widgets/landing/documents";
import Footer from "@/widgets/landing/footer";
import Heritage from "@/widgets/landing/heritage";
import Institute from "@/widgets/landing/institute";
import InstituteServices from "@/widgets/landing/institute-services";
import Laboratory from "@/widgets/landing/laboratory";
import Quality from "@/widgets/landing/quality";
import Partners from "@/widgets/landing/partners";
import WhatIsThis from "@/widgets/landing/what-is-this";

export default function Home() {
  return (
    <main>
      <Hero />
      <Directions />
      <WhatIsThis />
      <InstituteServices />
      <Quality />
      <Laboratory />
      <Activities />
      <Heritage />
      <Institute />
      <Documents />
      <Advantages />
      <Partners />
      <Contacts />
      <Footer />
    </main>
  );
}
