/* 静态正文始终可读；脚本仅增强导航、筛选与动效。 */
(() => {
  const nav = document.querySelector("#primary-nav");
  const toggle = document.querySelector(".nav-toggle");
  const links = [...nav.querySelectorAll("a")];
  const sections = links.map((link) => document.getElementById(link.hash.slice(1)));
  const cards = [...document.querySelectorAll(".project[data-group]")];
  const filters = [...document.querySelectorAll("[data-filter]")];
  const mobile = matchMedia("(max-width:900px)");
  const reduced = matchMedia("(prefers-reduced-motion:reduce)");
  document.documentElement.classList.add("enhanced");

  function menu(open, restore = false) {
    nav.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "关闭导航" : "打开导航");
    if (restore) toggle.focus();
  }
  toggle.addEventListener("click", () => menu(!nav.classList.contains("open")));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("open")) menu(false, true);
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".masthead")) menu(false);
  });
  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    menu(false);
    if (mobile.matches) {
      const section = document.getElementById(link.hash.slice(1));
      section.setAttribute("tabindex", "-1");
      section.focus({ preventScroll: true });
    }
  });
  mobile.addEventListener("change", () => menu(false));
  const clearTech = document.querySelector("#clear-tech-filter");
  const status = document.querySelector("#filter-status");
  const techButtons = [];
  function filter(group, tech = null) {
    filters.forEach((btn) => btn.setAttribute("aria-pressed", String(!tech && btn.dataset.filter === group)));
    techButtons.forEach(({ button, name }) => button.setAttribute("aria-pressed", String(name === tech)));
    cards.forEach((card) => {
      card.hidden = tech
        ? !techButtons.some((entry) => entry.card === card && entry.name === tech)
        : group !== "all" && !card.dataset.group.split(/\s+/).includes(group);
    });
    const count = cards.filter((card) => !card.hidden).length;
    status.textContent = tech ? `显示 ${count} 个 ${tech} 项目` : `显示 ${count} 个项目`;
    clearTech.hidden = !tech;
    if (tech) {
      clearTech.textContent = `${tech} · ${count} 个项目  ×`;
      clearTech.setAttribute("aria-label", `清除 ${tech} 筛选，显示全部项目`);
    }
  }
  function showAll() {
    filter("all");
    filters.find((btn) => btn.dataset.filter === "all").focus();
  }
  clearTech.addEventListener("click", showAll);
  filters.forEach((btn) => btn.addEventListener("click", () => filter(btn.dataset.filter)));
  // Without JavaScript the same labels remain readable as ordinary list items.
  document.querySelectorAll(".tags [data-technology]").forEach((tag) => {
    const name = tag.dataset.technology;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = tag.textContent;
    button.setAttribute("aria-label", `${button.textContent}: filter ${name} projects`);
    button.setAttribute("aria-controls", "project-list");
    button.setAttribute("aria-pressed", "false");
    tag.replaceChildren(button);
    techButtons.push({ button, name, card: tag.closest(".project") });
    button.addEventListener("click", () => {
      if (button.getAttribute("aria-pressed") === "true") return showAll();
      filter(null, name);
      clearTech.focus({ preventScroll: true });
      document.querySelector("#projects").scrollIntoView({ block: "start" });
    });
  });
  function restoreTarget() {
    const target = document.getElementById(location.hash.slice(1));
    if (target?.closest(".project[hidden]")) {
      filter("all");
      target.scrollIntoView();
    }
  }
  addEventListener("hashchange", restoreTarget);
  restoreTarget();
  // 大屏下最后两个章节可能共用同一滚动终点；显式锚点优先于页底推断。
  let intended = location.hash;
  addEventListener("hashchange", () => {
    intended = location.hash;
    sync();
  });
  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (link) {
      intended = link.hash;
      sync();
    }
  });
  function releaseIntent() {
    intended = "";
    sync();
  }
  addEventListener("wheel", releaseIntent, { passive: true });
  addEventListener("touchmove", releaseIntent, { passive: true });
  addEventListener("keydown", (event) => {
    if (["PageUp", "PageDown", "ArrowDown", "ArrowUp", "Home", "End", " "].includes(event.key))
      releaseIntent();
  });
  let scheduled = false;
  function active() {
    scheduled = false;
    const limit = Math.min(innerHeight * 0.28, 210);
    let index = 0;
    sections.forEach((section, i) => {
      if (section.getBoundingClientRect().top <= limit) index = i;
    });
    if (scrollY + innerHeight >= document.documentElement.scrollHeight - 3) {
      const requested = links.findIndex((link) => link.hash === intended);
      index =
        requested >= 0 && sections[requested].getBoundingClientRect().bottom > limit
          ? requested
          : sections.length - 1;
    }
    links.forEach((link, i) => {
      if (i === index) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }
  function sync() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(active);
    }
  }
  addEventListener("scroll", sync, { passive: true });
  addEventListener("resize", sync);
  active();
  if ("IntersectionObserver" in window && !reduced.matches) {
    const reveal = new IntersectionObserver(
      (entries) =>
        entries.forEach(({ target, isIntersecting }) => {
          if (isIntersecting) {
            target.classList.add("reveal-title");
            reveal.unobserve(target);
          }
        }),
      { threshold: 0.25 },
    );
    document.querySelectorAll(".section-head").forEach((el) => reveal.observe(el));
  }
})();
