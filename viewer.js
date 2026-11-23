/* 只增强明确标注的图片链接；无 JS、修饰键和新标签操作走普通 URL。 */
(() => {
  const viewer = document.getElementById("viewer");
  if (!viewer || typeof viewer.showModal !== "function") return;
  const img = viewer.querySelector("img");
  const original = viewer.querySelector(".viewer-foot a");
  const zoom = viewer.querySelector(".zoom");
  const canvas = viewer.querySelector(".viewer-canvas");
  let opener;
  function setZoom(active) {
    zoom.setAttribute("aria-pressed", String(active));
    canvas.classList.toggle("native-size", active);
    if (active) canvas.tabIndex = 0;
    else canvas.removeAttribute("tabindex");
    canvas.scrollTo(0, 0);
  }
  zoom.addEventListener("click", () => {
    const active = !canvas.classList.contains("native-size");
    setZoom(active);
    if (active) canvas.focus({ preventScroll: true });
  });
  document.addEventListener("click", (event) => {
    const a = event.target.closest("a[data-plate]");
    if (
      !a ||
      event.defaultPrevented ||
      event.button !== 0 ||
      event.ctrlKey ||
      event.metaKey ||
      event.altKey ||
      event.shiftKey
    )
      return;
    event.preventDefault();
    const figure = a.closest("figure,article");
    const caption = figure?.querySelector(".plate-head b,h3")?.textContent.trim();
    viewer.querySelector("h2").textContent = caption || "工程图版";
    img.alt = figure?.querySelector("img")?.alt || caption || "工程图版";
    setZoom(false);
    img.src = a.href;
    original.href = a.href;
    opener = a;
    viewer.showModal();
    document.documentElement.classList.add("viewing-plate");
  });
  viewer.addEventListener("click", (event) => {
    if (event.target !== viewer) return;
    const r = viewer.getBoundingClientRect();
    if (
      event.clientX < r.left ||
      event.clientX > r.right ||
      event.clientY < r.top ||
      event.clientY > r.bottom
    )
      viewer.close();
  });
  viewer.addEventListener("close", () => {
    // 关闭事件排队期间可能已经打开下一张图。
    if (viewer.open) return;
    document.documentElement.classList.remove("viewing-plate");
    img.removeAttribute("src");
    opener?.focus({ preventScroll: true });
  });
})();

// 核桃扫层：跟随系统动效偏好，并允许访客单独暂停本图版。
for (const button of document.querySelectorAll('[data-sweep-toggle]')) {
  const source = button.closest('article,figure').querySelector('.ct-sweep source');
  const preference = matchMedia('(prefers-reduced-motion: no-preference)');
  function setMotion(on) {
    source.media = on ? 'all' : 'not all';
    button.textContent = on ? '显示静态图' : '播放扫层动图';
    button.hidden = false;
  }
  setMotion(preference.matches);
  preference.addEventListener('change', () => setMotion(preference.matches));
  button.addEventListener('click', () => setMotion(source.media !== 'all'));
}
