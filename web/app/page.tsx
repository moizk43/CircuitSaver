import Navbar from "@/components/layout/Navbar";
import HeroSection from "@/components/landing/HeroSection";
import ImpactSlider from "@/components/landing/ImpactSlider";
import MissionSection from "@/components/landing/MissionSection";

export default function LandingPage() {
  return (
    <main>
      <Navbar />
      <HeroSection />
      <MissionSection />
      <ImpactSlider />

      <footer className="border-t border-gray-100 py-10 px-6 bg-white">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row
                        items-center justify-between gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-2 font-semibold text-gray-700">
            <span className="w-5 h-5 rounded-lg bg-brand-500 inline-block" />
            Verdant
          </div>
          <p>© {new Date().getFullYear()} Verdant Energy, Inc. All rights reserved.</p>
          <p className="text-brand-500 font-medium">Built for a greener planet.</p>
        </div>
      </footer>
    </main>
  );
}
