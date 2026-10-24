
import {
  ArrowRight,
  BadgeCheck,
  CalendarCheck2,
  CreditCard,
  Headphones,
  MapPinned,
  PlaneTakeoff,
  ShieldCheck,
  Sparkles,
  TicketCheck,
} from "lucide-react";

import Navbar from "../components/Navbar";
import FlightSearch from "../components/FlightSearch";

const features = [
  {
    icon: MapPinned,
    title: "Discover destinations",
    description:
      "Explore routes, compare travel options, and find the journey that suits you.",
  },
  {
    icon: CalendarCheck2,
    title: "Flexible flight search",
    description:
      "Search one-way or round-trip journeys with dates, travellers, and cabin preferences.",
  },
  {
    icon: ShieldCheck,
    title: "Secure booking workflow",
    description:
      "Designed for server-side validation, reservation management, and secure payment verification.",
  },
];

const steps = [
  {
    number: "01",
    title: "Search your flight",
    description:
      "Choose where you want to go and when you want to travel.",
  },
  {
    number: "02",
    title: "Select your journey",
    description:
      "Review fares, flight details, and available seats.",
  },
  {
    number: "03",
    title: "Book with confidence",
    description:
      "Complete test checkout and manage your demo reservation.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-[#f5f8ff]">

      {/* ================= HERO SECTION ================= */}
      <section className="relative isolate bg-[#123b7a] pb-10 text-white">

        {/* Background image */}
        <div
          className="pointer-events-none absolute inset-0 -z-20 bg-cover bg-center"
          style={{
            backgroundImage:
              'url("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=2200&q=85")',
          }}
        />

        {/* Darker overlay for readable text */}
        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-[#071e45]/75 via-[#123e7c]/60 to-[#071d51]/95" />

        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-r from-[#061b3b]/30 via-transparent to-[#061b3b]/35" />

        {/* Outer container */}
        <div className="relative mx-auto max-w-[1600px] px-3 pb-5 pt-4 sm:px-6 sm:pt-7 lg:px-10 lg:pt-10">

          {/* White bordered frame */}
          <div className="relative rounded-[28px] border-2 border-white/80 pb-7 shadow-[0_20px_80px_rgba(0,20,80,0.15)] sm:rounded-[36px] sm:pb-9">

            <Navbar />

            {/* Hero content */}
            <div className="relative mx-auto flex max-w-6xl flex-col items-center px-5 pb-5 pt-12 text-center sm:px-8 sm:pt-16 lg:pt-20">

              {/* Top badge */}
              <div className="hero-fade-in inline-flex items-center gap-2 rounded-full border border-white/40 bg-[#092f65]/50 px-5 py-2.5 text-xs font-semibold text-white shadow-lg backdrop-blur-md sm:text-sm">
                <Sparkles
                  size={16}
                  className="text-sky-200"
                />
                A better way to explore the skies
              </div>

              {/* Main heading */}
              <div className="hero-fade-in-delay mt-7 max-w-4xl">

                <h1 className="text-[clamp(2.5rem,5.2vw,4.8rem)] font-extrabold leading-[1.1] tracking-[-0.045em] text-white drop-shadow-[0_5px_18px_rgba(0,15,45,0.65)]">

                  The world is waiting.

                  <span className="mt-2 block text-white">
                    Let&apos;s take off.
                  </span>

                </h1>

                <p className="mx-auto mt-6 max-w-2xl text-sm font-medium leading-7 text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.65)] sm:text-base lg:text-lg">
                  Discover new destinations, compare flights,
                  and plan your next unforgettable journey —
                  all in one beautiful place.
                </p>

              </div>

              {/* Explore button */}
              <a
                href="#flights"
                className="mt-8 inline-flex items-center gap-2 rounded-full border border-white/50 bg-[#0a3775]/70 px-7 py-3.5 text-sm font-semibold text-white shadow-lg backdrop-blur-lg transition duration-300 hover:-translate-y-1 hover:bg-blue-700"
              >
                Explore flights
                <ArrowRight size={18} />
              </a>

              {/* Trust badges */}
              <div className="mt-10 flex flex-wrap items-center justify-center gap-3 sm:mt-12">

                {[
                  {
                    icon: BadgeCheck,
                    label: "Easy flight search",
                  },
                  {
                    icon: TicketCheck,
                    label: "Simple reservations",
                  },
                  {
                    icon: ShieldCheck,
                    label: "Secure test payments",
                  },
                ].map(({ icon: Icon, label }) => (
                  <span
                    key={label}
                    className="inline-flex items-center gap-2 rounded-full border border-white/35 bg-[#092f65]/55 px-4 py-2.5 text-xs font-semibold text-white shadow-sm backdrop-blur-md"
                  >
                    <Icon
                      size={15}
                      className="text-sky-200"
                    />
                    {label}
                  </span>
                ))}

              </div>
            </div>

            {/* ================= FLIGHT SEARCH CARD ================= */}
            <div className="relative z-20 mx-auto mt-10 max-w-[1450px] px-4 sm:px-7 lg:mt-12 lg:px-10">
              <FlightSearch />
            </div>

          </div>
        </div>
      </section>

      {/* ================= FEATURES SECTION ================= */}
      <section
        id="features"
        className="mx-auto max-w-7xl scroll-mt-20 px-5 pb-24 pt-20 sm:px-8 lg:pt-24"
      >

        <div className="mx-auto max-w-2xl text-center">

          <span className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-xs font-bold uppercase tracking-widest text-blue-700">
            <PlaneTakeoff size={15} />
            Why AeroSky
          </span>

          <h2 className="mt-6 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Your journey, made simpler.
          </h2>

          <p className="mt-4 leading-7 text-slate-600">
            Thoughtfully designed flight discovery and booking tools,
            built around a smooth travel experience.
          </p>

        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">

          {features.map(
            ({ icon: Icon, title, description }) => (
              <article
                key={title}
                className="group rounded-[28px] border border-slate-200 bg-white p-8 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl"
              >

                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-700 transition group-hover:bg-blue-700 group-hover:text-white">
                  <Icon size={25} />
                </div>

                <h3 className="mt-6 text-xl font-bold text-slate-900">
                  {title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  {description}
                </p>

              </article>
            )
          )}

        </div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section
        id="how-it-works"
        className="scroll-mt-20 bg-white py-20 sm:py-24"
      >

        <div className="mx-auto max-w-7xl px-5 sm:px-8">

          <div className="max-w-2xl">

            <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
              Three simple steps
            </span>

            <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              From inspiration to takeoff.
            </h2>

            <p className="mt-4 text-slate-600">
              A streamlined booking journey designed to
              keep important details clear.
            </p>

          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-3">

            {steps.map((step) => (
              <article
                key={step.number}
                className="rounded-3xl border border-slate-100 bg-slate-50 p-7"
              >

                <span className="text-4xl font-black tracking-tight text-blue-200">
                  {step.number}
                </span>

                <h3 className="mt-5 text-lg font-bold text-slate-900">
                  {step.title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  {step.description}
                </p>

              </article>
            ))}

          </div>
        </div>
      </section>

      {/* ================= CTA SECTION ================= */}
      <section className="px-5 py-20 sm:px-8">

        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 rounded-[32px] bg-gradient-to-r from-blue-800 to-sky-700 px-8 py-12 text-white sm:px-12 md:flex-row md:items-center">

          <div>

            <h2 className="text-2xl font-bold sm:text-3xl">
              Your next adventure starts here.
            </h2>

            <p className="mt-3 max-w-xl text-sm leading-7 text-blue-100">
              Choose your destination and start planning
              your journey with AeroSky.
            </p>

          </div>

          <a
            href="#flights"
            className="inline-flex shrink-0 items-center gap-2 rounded-full bg-white px-6 py-3.5 text-sm font-bold text-blue-800 transition hover:bg-blue-50"
          >
            Find flights
            <ArrowRight size={17} />
          </a>

        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="border-t border-slate-200 bg-white">

        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 px-5 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:px-8">

          <div className="flex items-center gap-2 font-bold text-blue-800">
            <PlaneTakeoff size={20} />
            <span className="text-lg">AeroSky.</span>
          </div>

          <p>
            Demo flight booking platform · Built with React & FastAPI
          </p>

          <div className="flex items-center gap-4">
            <CreditCard size={18} />
            <Headphones size={18} />
            <span>
              © {new Date().getFullYear()} AeroSky
            </span>
          </div>

        </div>
      </footer>

    </div>
  );
}
