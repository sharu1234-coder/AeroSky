

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { ArrowUpRight, Menu, PlaneTakeoff, UserRound, X } from "lucide-react";

const links = [
  { label: "Flights", href: "#flights" },
  { label: "Why AeroSky", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  function handleLogout() {
    logout();
    queryClient.clear();
    setMenuOpen(false);
    navigate("/", { replace: true });
  }

  return (
    <header className="relative z-30 flex items-center justify-between gap-4 px-5 py-5 sm:px-9 lg:px-12">
      <a href="#" className="flex items-center gap-2.5 text-white">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur-md">
          <PlaneTakeoff size={23} strokeWidth={2.3} />
        </span>
        <span className="text-2xl font-bold tracking-tight">
          AeroSky<span className="text-sky-200">.</span>
        </span>
      </a>

      <nav className="hidden items-center gap-9 lg:flex">
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className="text-sm font-medium text-white/85 transition hover:text-white"
          >
            {link.label}
          </a>
        ))}
      </nav>

      <div className="hidden items-center gap-3 sm:flex">
        <a
          href="#flights"
          className="inline-flex items-center gap-2 rounded-full border border-white/40 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur-md transition hover:bg-white/20"
        >
          Book a Flight <ArrowUpRight size={15} />
        </a>
        {isAuthenticated ? (
          <>
            <Link
              to="/my-bookings"
              className="text-sm font-semibold text-white hover:text-sky-200"
            >
              My Bookings
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full border border-white/40 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/20"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 text-sm font-semibold text-white hover:text-sky-200"
            >
              <UserRound size={18} />
              Login
            </Link>
            <Link
              to="/register"
              className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-blue-700 hover:bg-sky-100"
            >
              Sign Up
            </Link>
          </>
        )}
      </div>

      <button
        type="button"
        className="rounded-xl border border-white/30 p-2.5 text-white lg:hidden"
        aria-label={menuOpen ? "Close menu" : "Open menu"}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        {menuOpen ? <X size={23} /> : <Menu size={23} />}
      </button>

      {menuOpen && (
        <nav className="absolute left-5 right-5 top-[82px] z-50 flex flex-col gap-1 rounded-2xl border border-white/20 bg-slate-900/95 p-3 shadow-2xl backdrop-blur-xl lg:hidden">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="rounded-xl px-4 py-3 text-sm font-medium text-white hover:bg-white/10"
            >
              {link.label}
            </a>
          ))}
          <a
            href="#flights"
            onClick={() => setMenuOpen(false)}
            className="rounded-xl bg-blue-600 px-4 py-3 text-center text-sm font-semibold text-white"
          >
            Book a Flight
          </a>

          {isAuthenticated ? (
            <>
              <Link
                to="/my-bookings"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl px-4 py-3 text-sm font-semibold text-white hover:bg-white/10"
              >
                My Bookings
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-xl px-4 py-3 text-left text-sm font-semibold text-white hover:bg-white/10"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl px-4 py-3 text-sm font-semibold text-white hover:bg-white/10"
              >
                Login
              </Link>
              <Link
                to="/register"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl px-4 py-3 text-sm font-semibold text-white hover:bg-white/10"
              >
                Create Account
              </Link>
            </>
          )}
        </nav>
      )}
    </header>
  );
}
