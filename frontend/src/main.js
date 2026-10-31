const WORK_TYPES = {
  "Диагностика и ТО": ["Плановое ТО", "Диагностика", "Замена расходников", "Подготовка к сезону"],
  "Детейлинг и керамика": ["Детейлинг", "Полировка ЛКП", "Керамическое покрытие", "Мойка премиум"],
  "Антигравий PPF": ["Оклейка PPF", "Зоны риска", "Полный кузов", "Замена плёнки"],
  "Кузов и цвет": ["Кузовной ремонт", "Локальная покраска", "Подбор эмали", "Удаление сколов"],
  "Салон и кожа": ["Реставрация кожи", "Алькантара", "Дерево и хром", "Химчистка салона"],
  "Сезонное сопровождение": ["Подготовка к сезону", "Хранение", "Выезд мастера", "Персональный слот"],
};

const FALLBACK_SERVICES = [
  { title: "Диагностика и ТО", description: "Регламент марки, без универсальных решений" },
  { title: "Детейлинг и керамика", description: "ЛКП, полировка, защитные покрытия" },
  { title: "Антигравий PPF", description: "Полиуретан на зоны риска или весь кузов" },
  { title: "Кузов и цвет", description: "Локальный ремонт с сохранением заводской фактуры" },
  { title: "Салон и кожа", description: "Реставрация кожи, алькантары, дерева и хрома" },
  { title: "Сезонное сопровождение", description: "Хранение, выдача и персональный слот" },
];

function startScene(canvas) {
  if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const ctx = canvas.getContext("2d", { alpha: true });
  if (!ctx) return;

  const stars = Array.from({ length: 70 }, () => ({
    x: Math.random(),
    y: Math.random() * 0.42,
    r: 0.4 + Math.random() * 1.3,
    a: 0.15 + Math.random() * 0.55,
  }));
  const lamps = Array.from({ length: 18 }, () => ({
    x: 0.18 + Math.random() * 0.64,
    y: 0.58 + Math.random() * 0.08,
    s: 0.8 + Math.random() * 1.6,
    warm: Math.random() > 0.35,
  }));
  const dust = Array.from({ length: 10 }, () => ({
    x: Math.random(),
    y: 0.2 + Math.random() * 0.5,
    r: 40 + Math.random() * 90,
    vx: (Math.random() - 0.5) * 0.00008,
    a: 0.03 + Math.random() * 0.04,
  }));

  const fit = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  fit();
  window.addEventListener("resize", fit);

  const tick = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    ctx.clearRect(0, 0, w, h);
    for (const star of stars) {
      ctx.fillStyle = `rgba(255, 246, 222, ${star.a})`;
      ctx.fillRect(star.x * w, star.y * h, star.r, star.r);
    }
    for (const orb of dust) {
      orb.x += orb.vx;
      if (orb.x < -0.1 || orb.x > 1.1) orb.vx *= -1;
      const x = orb.x * w;
      const y = orb.y * h;
      const g = ctx.createRadialGradient(x, y, 2, x, y, orb.r);
      g.addColorStop(0, `rgba(255, 186, 122, ${orb.a})`);
      g.addColorStop(1, "rgba(196, 165, 116, 0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, orb.r, 0, Math.PI * 2);
      ctx.fill();
    }
    for (const lamp of lamps) {
      const x = lamp.x * w;
      const y = lamp.y * h;
      const color = lamp.warm ? "255, 186, 122" : "232, 213, 163";
      const g = ctx.createRadialGradient(x, y, 0, x, y, 7 * lamp.s);
      g.addColorStop(0, `rgba(${color}, .7)`);
      g.addColorStop(1, `rgba(${color}, 0)`);
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, 7 * lamp.s, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function esc(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function money(value) {
  return new Intl.NumberFormat("ru-RU").format(Number(value)) + " ₽";
}

function tracker() {
  const started = Date.now();
  const visitsKey = "da_returns";
  if (!sessionStorage.getItem("da_session")) {
    localStorage.setItem(visitsKey, String(Number(localStorage.getItem(visitsKey) || "0") + 1));
    sessionStorage.setItem("da_session", "1");
  }
  const metrics = {
    buttons: [],
    hovers: {},
    hoverStart: {},
    returns: Number(localStorage.getItem(visitsKey) || "1"),
  };
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") metrics.returns += 1;
  });
  document.addEventListener("click", (event) => {
    const el = event.target.closest("button, summary, a, select, input[type=range]");
    if (!el) return;
    metrics.buttons.push({
      name: el.id || el.name || el.tagName.toLowerCase(),
      text: (el.innerText || el.value || "").slice(0, 80),
      t: Date.now() - started,
    });
  });
  document.addEventListener("pointerenter", (event) => {
    const el = event.target;
    if (!(el instanceof HTMLElement) || !el.closest("form")) return;
    const name = el.id || el.name;
    if (!name) return;
    metrics.hoverStart[name] = Date.now();
  }, true);
  document.addEventListener("pointerleave", (event) => {
    const el = event.target;
    if (!(el instanceof HTMLElement)) return;
    const name = el.id || el.name;
    if (!name || !metrics.hoverStart[name]) return;
    metrics.hovers[name] = (metrics.hovers[name] || 0) + (Date.now() - metrics.hoverStart[name]);
    delete metrics.hoverStart[name];
  }, true);
  return { started, metrics };
}

function fillWorkTypes(serviceTitle, workTypeSelect) {
  const types = WORK_TYPES[serviceTitle] || [];
  if (!serviceTitle || !types.length) {
    workTypeSelect.innerHTML = '<option value="">Сначала выберите услугу</option>';
    workTypeSelect.disabled = true;
    workTypeSelect.value = "";
    return;
  }
  workTypeSelect.disabled = false;
  workTypeSelect.innerHTML = '<option value="">Выберите тип работ</option>' + types.map((item) => (
    `<option value="${esc(item)}">${esc(item)}</option>`
  )).join("");
}

function syncService(title, serviceSelect, box, workTypeSelect) {
  serviceSelect.value = title;
  box.querySelectorAll(".svc").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.service === title);
  });
  fillWorkTypes(title, workTypeSelect);
}

function renderServices(items, serviceSelect, box, workTypeSelect) {
  box.innerHTML = items.map((item) => {
    const title = item.title || item.key || "";
    return `<button type="button" class="svc" data-service="${esc(title)}">
      <h3>${esc(title)}</h3>
      <p>${esc(item.description || "")}</p>
    </button>`;
  }).join("");
  serviceSelect.innerHTML = '<option value="">Выберите услугу</option>' + items.map((item) => {
    const title = item.title || item.key || "";
    return `<option value="${esc(title)}">${esc(title)}</option>`;
  }).join("");
  fillWorkTypes("", workTypeSelect);
  box.querySelectorAll(".svc").forEach((card) => {
    card.addEventListener("click", () => {
      syncService(card.dataset.service || "", serviceSelect, box, workTypeSelect);
    });
  });
  serviceSelect.addEventListener("change", () => {
    syncService(serviceSelect.value, serviceSelect, box, workTypeSelect);
  });
}

async function loadAdmin(budget, budgetLabel, serviceSelect, servicesBox, workTypeSelect) {
  const apply = (data) => {
    const min = Number(data.budget_min || 200000);
    const max = Number(data.budget_max || 6000000);
    const step = Number(data.budget_step || 50000);
    budget.min = min;
    budget.max = max;
    budget.step = step;
    budget.value = Math.round((min + max) / 2 / step) * step;
    budgetLabel.textContent = money(budget.value);
    const services = data.services && data.services.length ? data.services : FALLBACK_SERVICES;
    renderServices(services, serviceSelect, servicesBox, workTypeSelect);
  };
  try {
    const res = await fetch("/api/admin");
    if (!res.ok) throw new Error(String(res.status));
    apply(await res.json());
  } catch {
    apply({ budget_min: "200000", budget_max: "6000000", budget_step: "50000", services: FALLBACK_SERVICES });
  }
}

function boot() {
  startScene(document.getElementById("scene"));
  const { started, metrics } = tracker();
  const form = document.getElementById("lead-form");
  const budget = document.getElementById("budget");
  const budgetLabel = document.getElementById("budget-label");
  const serviceSelect = document.getElementById("service");
  const workTypeSelect = document.getElementById("work_type");
  const servicesBox = document.getElementById("services");
  const err = document.getElementById("err");
  const thanks = document.getElementById("thanks");
  budget.addEventListener("input", () => {
    budgetLabel.textContent = money(budget.value);
  });
  fillWorkTypes("", workTypeSelect);
  loadAdmin(budget, budgetLabel, serviceSelect, servicesBox, workTypeSelect);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    err.textContent = "";
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    const body = Object.fromEntries(new FormData(form).entries());
    const pack = {
      ...body,
      behavior: {
        time_on_page_ms: Date.now() - started,
        return_count: metrics.returns,
        buttons_clicked: metrics.buttons,
        cursor_hovers: Object.entries(metrics.hovers).map(([name, ms]) => ({ name, ms })),
        user_agent: navigator.userAgent,
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        referrer: document.referrer,
        page_url: location.href,
        tech: {
          visibility: document.visibilityState,
          platform: navigator.platform,
          vertical: "elite-autoservice",
        },
      },
    };
    try {
      const res = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pack),
      });
      if (!res.ok) throw new Error("сервер ответил " + res.status);
      form.hidden = true;
      thanks.hidden = false;
    } catch {
      err.textContent = "Не удалось отправить заявку. Попробуйте ещё раз.";
      btn.disabled = false;
    }
  });
}

boot();
