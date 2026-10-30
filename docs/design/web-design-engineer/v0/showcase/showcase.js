(() => {
  const root = document.documentElement;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const home = document.getElementById("home-page");
  const auth = document.getElementById("auth-page");
  const header = document.querySelector(".site-header");
  const form = document.getElementById("auth-form");
  const mobileMenu = document.getElementById("mobile-menu");
  const mobileToggle = document.getElementById("mobile-menu-toggle");
  const tweaks = document.getElementById("tweaks");
  const tweaksTrigger = document.getElementById("tweaks-trigger");
  const pageSelect = document.getElementById("page-select");
  const themeSelect = document.getElementById("theme-select");
  const motionSelect = document.getElementById("motion-select");
  const progress = document.querySelector(".progress-line");
  let authMode = false;
  let submitTimer = null;
  let scrollQueued = false;
  const pointer = { x: 0, y: 0, currentX: 0, currentY: 0 };

  function setMobile(open) {
    mobileMenu.hidden = !open;
    mobileToggle.setAttribute("aria-expanded", String(open));
    mobileToggle.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
    if (!open && mobileMenu.contains(document.activeElement))
      mobileToggle.focus({ preventScroll: true });
  }

  function setTweaks(open) {
    tweaks.hidden = !open;
    tweaksTrigger.setAttribute("aria-expanded", String(open));
    if (!open && tweaks.contains(document.activeElement))
      tweaksTrigger.focus({ preventScroll: true });
  }

  function updateScroll() {
    scrollQueued = false;
    header.classList.toggle("scrolled", window.scrollY > 28 || authMode);
    const length = document.documentElement.scrollHeight - window.innerHeight;
    const fraction =
      authMode || length <= 0 ? 0 : Math.min(1, window.scrollY / length);
    progress.style.transform = `scaleX(${fraction})`;
  }

  document.addEventListener(
    "scroll",
    () => {
      if (!scrollQueued) {
        scrollQueued = true;
        requestAnimationFrame(updateScroll);
      }
    },
    { passive: true },
  );

  function resetForm() {
    clearTimeout(submitTimer);
    form.reset();
    const submit = document.getElementById("auth-submit");
    submit.disabled = false;
    submit.classList.remove("busy");
    document.getElementById("password").type = "password";
    const showPassword = document.getElementById("toggle-password");
    showPassword.setAttribute("aria-pressed", "false");
    showPassword.setAttribute("aria-label", "显示密码");
    document.getElementById("auth-error").hidden = true;
  }

  function route() {
    const key = location.hash.slice(1) || "home";
    authMode = key === "login" || key === "register";
    document.body.classList.toggle("auth-mode", authMode);
    home.hidden = authMode;
    auth.hidden = !authMode;
    setMobile(false);
    if (authMode) {
      resetForm();
      const registering = key === "register";
      document.querySelectorAll(".register-field").forEach((element) => {
        element.hidden = !registering;
        element.querySelectorAll("input").forEach((input) => {
          input.disabled = !registering;
        });
      });
      document.getElementById("auth-title").textContent = registering
        ? "开启新的探索"
        : "欢迎回来";
      document.getElementById("auth-description").textContent = registering
        ? "创建账户，让每一次灵感有所归属。"
        : "继续你的探索，让研究向前一步。";
      document.querySelector("#auth-submit > span").textContent = registering
        ? "创建账户，预览工作台"
        : "登录并进入工作台";
      document.getElementById("auth-switch").replaceChildren();
      const switchText = document.createTextNode(
        registering ? "已有账户？" : "还没有账户？",
      );
      const switchLink = document.createElement("a");
      switchLink.href = registering ? "#login" : "#register";
      switchLink.textContent = registering ? "返回登录 ↗" : "创建新账户 ↗";
      document.getElementById("auth-switch").append(switchText, switchLink);
      document.title = (registering ? "注册" : "登录") + " · 研知协作";
      pageSelect.value = key;
      window.scrollTo({ top: 0, behavior: "instant" });
    } else {
      document.title = "研知协作 · 让探索，越过边界";
      pageSelect.value = "home";
      const target = ["home", "capabilities", "workspace", "workflow"].includes(
        key,
      )
        ? document.getElementById(key)
        : document.getElementById("home");
      requestAnimationFrame(() => {
        window.scrollTo({
          top: Math.max(
            0,
            target.getBoundingClientRect().top +
              window.scrollY -
              (key === "home" ? 0 : 100),
          ),
          behavior:
            reducedMotion.matches || root.dataset.motion === "static"
              ? "instant"
              : "smooth",
        });
      });
    }
    updateScroll();
    requestAnimationFrame(() => fieldManager.refresh());
  }

  window.addEventListener("hashchange", route);
  document.querySelectorAll("[data-section]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (!authMode && location.hash === link.hash) {
        event.preventDefault();
        route();
      }
    });
  });
  mobileToggle.addEventListener("click", () => setMobile(mobileMenu.hidden));
  tweaksTrigger.addEventListener("click", () => setTweaks(tweaks.hidden));
  document
    .getElementById("close-tweaks")
    .addEventListener("click", () => setTweaks(false));
  document
    .querySelectorAll("[data-open-tweaks]")
    .forEach((button) =>
      button.addEventListener("click", () => setTweaks(true)),
    );
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setTweaks(false);
      setMobile(false);
    }
  });
  document.addEventListener("click", (event) => {
    if (
      !tweaks.hidden &&
      !tweaks.contains(event.target) &&
      !tweaksTrigger.contains(event.target) &&
      !event.target.closest("[data-open-tweaks]")
    )
      setTweaks(false);
    if (
      !mobileMenu.hidden &&
      !mobileMenu.contains(event.target) &&
      !mobileToggle.contains(event.target)
    )
      setMobile(false);
  });

  function applyTheme(theme) {
    root.dataset.theme = theme;
    themeSelect.value = theme;
    try {
      sessionStorage.setItem("research-concept-theme", theme);
    } catch {
      /* Preview remains usable without storage. */
    }
    fieldManager.refresh();
  }
  document
    .getElementById("theme-toggle")
    .addEventListener("click", () =>
      applyTheme(root.dataset.theme === "dark" ? "light" : "dark"),
    );
  themeSelect.addEventListener("change", (event) =>
    applyTheme(event.target.value),
  );
  pageSelect.addEventListener("change", (event) => {
    if (event.target.value === "workspace") location.assign("experience.html");
    else location.hash = event.target.value;
    setTweaks(false);
  });
  motionSelect.addEventListener("change", (event) => {
    root.dataset.motion = event.target.value;
    fieldManager.refresh();
    if (event.target.value === "static")
      document
        .querySelectorAll(".reveal")
        .forEach((element) => element.classList.add("visible"));
  });

  document
    .getElementById("toggle-password")
    .addEventListener("click", (event) => {
      const password = document.getElementById("password");
      const showing = password.type === "password";
      password.type = showing ? "text" : "password";
      event.currentTarget.setAttribute(
        "aria-label",
        showing ? "隐藏密码" : "显示密码",
      );
      event.currentTarget.setAttribute("aria-pressed", String(showing));
    });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const submit = document.getElementById("auth-submit");
    if (submit.disabled) return;
    const registering = location.hash === "#register";
    const password = form.elements.password.value;
    const repeated = form.elements.password2.value;
    const error = document.getElementById("auth-error");
    if (registering && (password || repeated) && password !== repeated) {
      error.textContent = "两次密码输入不一致。预览时也可以全部留空。";
      error.hidden = false;
      return;
    }
    error.hidden = true;
    submit.disabled = true;
    submit.classList.add("busy");
    submit.querySelector("span").textContent = "正在进入工作区…";
    submitTimer = setTimeout(() => {
      // This is a visual concept, never an authentication endpoint.
      form.reset();
      location.assign("experience.html");
    }, 650);
  });

  if ("IntersectionObserver" in window) {
    root.classList.add("motion-ready");
    const revealObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -25px 0px" },
    );
    document
      .querySelectorAll(".reveal")
      .forEach((element) => revealObserver.observe(element));
  }

  // A code-native research field: no video, external libraries or image requests.
  // Use projected particles to carry depth, with the animation concentrated here.
  function createField(canvas) {
    const context = canvas.getContext("2d");
    if (!context) return null;
    let width = 0,
      height = 0,
      radius = 0;
    let intersecting = false;
    const count = window.innerWidth < 700 ? 850 : 1700;
    const points = [];
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const ringRadius = Math.sqrt(Math.max(0, 1 - y * y));
      const angle = goldenAngle * i;
      points.push({
        x: Math.cos(angle) * ringRadius,
        y,
        z: Math.sin(angle) * ringRadius,
        seed: (i * 0.61803398875) % 1,
      });
    }
    const resize = () => {
      const box = canvas.getBoundingClientRect();
      width = box.width;
      height = box.height;
      if (!width || !height) return;
      const ratio = Math.min(
        window.devicePixelRatio || 1,
        window.innerWidth < 700 ? 1.3 : 1.7,
      );
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      radius = Math.min(width * 0.31, height * 0.34);
      fieldManager.refresh();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    const visibilityObserver = new IntersectionObserver((entries) => {
      intersecting = entries[0].isIntersecting;
      fieldManager.refresh();
    });
    visibilityObserver.observe(canvas);
    function draw(time) {
      if (!width || !height) return;
      context.clearRect(0, 0, width, height);
      const light = root.dataset.theme === "light";
      const calm = root.dataset.motion === "calm";
      const speed = calm ? 0.000012 : 0.000028;
      const angle = time * speed + pointer.currentX * 0.18;
      const tilt = -0.25 + pointer.currentY * 0.11;
      const sin = Math.sin(angle),
        cos = Math.cos(angle);
      const sinTilt = Math.sin(tilt),
        cosTilt = Math.cos(tilt);
      const centerX = width * (canvas.id === "auth-field" ? 0.53 : 0.55);
      const centerY = height * 0.51;
      const glow = context.createRadialGradient(
        centerX,
        centerY,
        radius * 0.03,
        centerX,
        centerY,
        radius * 1.8,
      );
      glow.addColorStop(
        0,
        light ? "rgba(44,112,192,.055)" : "rgba(53,125,215,.14)",
      );
      glow.addColorStop(
        0.5,
        light ? "rgba(44,112,192,.025)" : "rgba(32,91,170,.07)",
      );
      glow.addColorStop(1, "rgba(32,91,170,0)");
      context.fillStyle = glow;
      context.fillRect(0, 0, width, height);
      function project(x, y, z, expansion = 1) {
        const rotatedX = x * cos - z * sin;
        const rotatedZ = x * sin + z * cos;
        const rotatedY = y * cosTilt - rotatedZ * sinTilt;
        const depth = y * sinTilt + rotatedZ * cosTilt;
        const perspective = 2.9 / (2.9 + depth * 0.45);
        return {
          x: centerX + rotatedX * radius * perspective * expansion,
          y: centerY + rotatedY * radius * perspective * expansion,
          depth,
        };
      }
      const projected = points.map((point) => ({
        ...project(point.x, point.y, point.z),
        seed: point.seed,
      }));
      // Sparse links trace the surface rather than turning the scene into a mesh wall.
      context.lineWidth = 0.55;
      for (let i = 0; i < projected.length - 13; i += 5) {
        const a = projected[i],
          b = projected[i + 13];
        if (a.depth > 0.6 || Math.abs(a.depth - b.depth) > 0.28) continue;
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        if (distance > radius * 0.21) continue;
        context.strokeStyle = light
          ? "rgba(35,101,174,.13)"
          : "rgba(99,161,224,.15)";
        context.beginPath();
        context.moveTo(a.x, a.y);
        context.lineTo(b.x, b.y);
        context.stroke();
      }
      projected.sort((a, b) => b.depth - a.depth);
      for (const point of projected) {
        const depthFactor = (1 - point.depth) / 2;
        const wave = 0.85 + Math.sin(time * 0.0007 + point.seed * 14) * 0.15;
        const opacity = (0.13 + depthFactor * 0.72) * wave;
        const size = 0.45 + depthFactor * 0.92;
        context.fillStyle = light
          ? `rgba(33,105,182,${opacity * 0.78})`
          : point.seed > 0.88
            ? `rgba(176,231,244,${opacity})`
            : `rgba(91,157,237,${opacity})`;
        context.beginPath();
        context.arc(point.x, point.y, size, 0, Math.PI * 2);
        context.fill();
      }
      // Two distinct orbital arcs communicate connection around the shared core.
      for (let ring = 0; ring < 2; ring++) {
        context.beginPath();
        for (let i = 0; i <= 220; i++) {
          const phase =
            (i / 220) * Math.PI * 2 + time * speed * (ring ? -0.5 : 0.45);
          const x = Math.cos(phase);
          const y = Math.sin(phase) * (ring ? 0.58 : -0.42);
          const z = Math.sin(phase) * (ring ? 0.78 : 0.9);
          const point = project(x, y, z, ring ? 1.24 : 1.4);
          i
            ? context.lineTo(point.x, point.y)
            : context.moveTo(point.x, point.y);
        }
        context.lineWidth = 0.7;
        context.strokeStyle = light
          ? "rgba(39,107,184,.2)"
          : "rgba(114,186,225,.27)";
        context.stroke();
        const phase = time * speed * (ring ? -1.2 : 1.5) + ring * 2.6;
        const p = project(
          Math.cos(phase),
          Math.sin(phase) * (ring ? 0.58 : -0.42),
          Math.sin(phase) * (ring ? 0.78 : 0.9),
          ring ? 1.24 : 1.4,
        );
        const spark = context.createRadialGradient(p.x, p.y, 0, p.x, p.y, 12);
        spark.addColorStop(
          0,
          light ? "rgba(53,117,202,.45)" : "rgba(174,227,255,.8)",
        );
        spark.addColorStop(
          0.2,
          light ? "rgba(53,117,202,.1)" : "rgba(117,185,255,.2)",
        );
        spark.addColorStop(1, "rgba(117,185,255,0)");
        context.fillStyle = spark;
        context.fillRect(p.x - 12, p.y - 12, 24, 24);
      }
    }
    return {
      draw,
      get active() {
        return intersecting && canvas.getBoundingClientRect().width > 0;
      },
    };
  }

  const fieldManager = {
    fields: [],
    frame: null,
    clock: 0,
    previous: 0,
    refresh() {
      for (const field of this.fields) if (field.active) field.draw(this.clock);
      if (
        !this.frame &&
        !document.hidden &&
        root.dataset.motion !== "static" &&
        !reducedMotion.matches &&
        this.fields.some((field) => field.active)
      ) {
        this.previous = 0;
        this.frame = requestAnimationFrame(tick);
      }
    },
  };
  function tick(now) {
    fieldManager.frame = null;
    if (
      document.hidden ||
      root.dataset.motion === "static" ||
      reducedMotion.matches
    )
      return;
    const active = fieldManager.fields.filter((field) => field.active);
    if (!active.length) return;
    const elapsed = fieldManager.previous
      ? Math.min(40, now - fieldManager.previous)
      : 16;
    fieldManager.previous = now;
    fieldManager.clock += elapsed;
    pointer.currentX += (pointer.x - pointer.currentX) * 0.035;
    pointer.currentY += (pointer.y - pointer.currentY) * 0.035;
    for (const field of active) field.draw(fieldManager.clock);
    fieldManager.frame = requestAnimationFrame(tick);
  }
  document.addEventListener(
    "pointermove",
    (event) => {
      if (event.pointerType === "touch") return;
      pointer.x = event.clientX / window.innerWidth - 0.5;
      pointer.y = event.clientY / window.innerHeight - 0.5;
    },
    { passive: true },
  );
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && fieldManager.frame) {
      cancelAnimationFrame(fieldManager.frame);
      fieldManager.frame = null;
    } else fieldManager.refresh();
  });
  reducedMotion.addEventListener("change", () => fieldManager.refresh());
  for (const canvas of document.querySelectorAll("canvas")) {
    const field = createField(canvas);
    if (field) fieldManager.fields.push(field);
  }
  if (reducedMotion.matches) {
    motionSelect.value = "static";
    root.dataset.motion = "static";
  }
  try {
    const theme = sessionStorage.getItem("research-concept-theme");
    if (theme === "light" || theme === "dark") applyTheme(theme);
  } catch {
    /* Storage is optional. */
  }
  route();
})();
