"use client";

/* Client islands. Everything on the page renders complete, final-state HTML on
   the server; these components only add behavior on top (scroll-step switching,
   the hero count-up, tab switching). With JavaScript off the page stays fully
   readable: steps and states render stacked, tabs render as stacked panels. */

import { useEffect, useId, useRef, useState, useSyncExternalStore, type KeyboardEvent, type ReactNode } from "react";

const reducedMotion = () =>
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const subscribeToHydration = () => () => {};
const clientIsHydrated = () => true;
const serverIsHydrated = () => false;

/** Sticky exhibit pane + stepped prose. stepToState maps a step index to the
    exhibit state it should display (defaults to the identity mapping). */
export function Scrolly({
  steps,
  states,
  stepToState,
  ariaLabel,
}: {
  steps: ReactNode[];
  states: ReactNode[];
  stepToState?: number[];
  ariaLabel: string;
}) {
  const [active, setActive] = useState(0);
  const enhanced = useSyncExternalStore(subscribeToHydration, clientIsHydrated, serverIsHydrated);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const stepEls = Array.from(root.querySelectorAll<HTMLElement>("[data-step]"));
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActive(Number((entry.target as HTMLElement).dataset.step));
          }
        }
      },
      { rootMargin: "-45% 0px -45% 0px" },
    );
    stepEls.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const stateIndex = stepToState ? stepToState[active] : active;

  return (
    <div className="scrolly" ref={rootRef} role="group" aria-label={ariaLabel}>
      <div className="scrolly-steps">
        {steps.map((step, index) => (
          <div
            key={index}
            data-step={index}
            className={`scrolly-step${index === active ? " active" : ""}`}
          >
            {step}
          </div>
        ))}
      </div>
      <div className="scrolly-sticky">
        <div className="scrolly-pane">
          {states.map((state, index) => (
            <div
              key={index}
              className={`scrolly-state${index === stateIndex ? " active" : ""}`}
              aria-hidden={enhanced ? index !== stateIndex : undefined}
            >
              {state}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/** Counts up once on first view. Server-renders the final value so the number
    is correct without JavaScript and for crawlers. */
export function CountUp({ value, className }: { value: number; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const done = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || done.current || reducedMotion()) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting) || done.current) return;
      done.current = true;
      observer.disconnect();
      const duration = 1400;
      const start = performance.now();
      const tick = (now: number) => {
        const progress = Math.min(1, (now - start) / duration);
        const eased = 1 - (1 - progress) ** 4;
        el.textContent = Math.round(value * eased).toLocaleString("en-US");
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [value]);

  return (
    <span ref={ref} className={className}>
      {value.toLocaleString("en-US")}
    </span>
  );
}

/** Fixed side rail listing the page's sections; highlights the one in view.
    Hidden below 1360px and without JavaScript (the route map after the hero
    covers jumping there). */
export function SectionNav({ sections }: { sections: { id: string; label: string }[] }) {
  const [current, setCurrent] = useState<string | null>(null);
  const [pastHero, setPastHero] = useState(false);

  useEffect(() => {
    const els = sections
      .map((section) => document.getElementById(section.id))
      .filter((el): el is HTMLElement => el !== null);
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setCurrent(entry.target.id);
        }
      },
      { rootMargin: "-35% 0px -55% 0px" },
    );
    els.forEach((el) => observer.observe(el));
    /* The rail stays hidden while the drenched hero fills the screen — it
       would float unreadably over the madder ground. */
    const hero = document.querySelector(".hero");
    const heroObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) setPastHero(!entry.isIntersecting);
    });
    if (hero) heroObserver.observe(hero);
    return () => {
      observer.disconnect();
      heroObserver.disconnect();
    };
  }, [sections]);

  return (
    <nav
      className={`siterail${pastHero ? " vis" : ""}`}
      aria-label="Sections of this page"
      aria-hidden={!pastHero}
      inert={!pastHero}
    >
      {sections.map((section) => (
        <a key={section.id} href={`#${section.id}`} aria-current={current === section.id || undefined}>
          {section.label}
        </a>
      ))}
    </nav>
  );
}

/** Accessible tab switcher. Without JavaScript all panels render stacked with
    their own headings; with it, one panel shows at a time. */
export function Tabs({
  labels,
  panels,
  defaultIndex = 0,
  ariaLabel,
}: {
  labels: string[];
  panels: ReactNode[];
  defaultIndex?: number;
  ariaLabel: string;
}) {
  const [selected, setSelected] = useState(defaultIndex);
  const baseId = useId();
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const selectAndFocus = (index: number) => {
    setSelected(index);
    tabRefs.current[index]?.focus();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    let next: number | null = null;
    if (event.key === "ArrowRight") next = (index + 1) % labels.length;
    if (event.key === "ArrowLeft") next = (index - 1 + labels.length) % labels.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = labels.length - 1;
    if (next === null) return;
    event.preventDefault();
    selectAndFocus(next);
  };

  /* Visibility is CSS-driven: with the `js` class on <html>, inactive panels
     hide; without JavaScript the tablist hides and all panels render stacked,
     each captioned by its data-label. */
  return (
    <div className="tabset">
      <div role="tablist" aria-label={ariaLabel} className="tab-labels">
        {labels.map((label, index) => (
          <button
            key={label}
            ref={(element) => { tabRefs.current[index] = element; }}
            id={`${baseId}-tab-${index}`}
            role="tab"
            aria-selected={index === selected}
            aria-controls={`${baseId}-panel-${index}`}
            tabIndex={index === selected ? 0 : -1}
            style={
              index === selected
                ? { borderColor: "var(--ink)", color: "var(--ink)", fontWeight: 600 }
                : undefined
            }
            onClick={() => setSelected(index)}
            onKeyDown={(event) => handleKeyDown(event, index)}
          >
            {label}
          </button>
        ))}
      </div>
      {panels.map((panel, index) => (
        <div
          key={index}
          id={`${baseId}-panel-${index}`}
          role="tabpanel"
          aria-labelledby={`${baseId}-tab-${index}`}
          className="tabpanel"
          data-label={labels[index]}
          data-active={index === selected || undefined}
        >
          {panel}
        </div>
      ))}
    </div>
  );
}
