(() => {
  const items = [...document.querySelectorAll("[data-item]")];
  const cmd = document.getElementById("cmd");
  const cmdQ = document.getElementById("cmd-q");
  const cmdList = document.getElementById("cmd-list");
  const help = document.getElementById("help");
  const catalog = items.map((el, i) => ({
    el,
    name: el.dataset.name,
    href: el.getAttribute("href"),
    id: String(i + 1).padStart(2, "0"),
    line:
      el.querySelector(".feature-line, .row-line")?.textContent.trim() ||
      el.dataset.name,
  }));

  let index = 0;
  let gPending = false;
  let cmdCursor = 0;

  const setActive = (next) => {
    if (!items.length) return;
    index = (next + items.length) % items.length;
    items.forEach((el, i) => el.classList.toggle("is-active", i === index));
    items[index].scrollIntoView({ block: "nearest", behavior: "smooth" });
  };

  const openActive = () => {
    const target = items[index];
    if (target) window.location.assign(target.href);
  };

  const matches = (query) => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter((item) =>
      (item.name + " " + item.line + " " + item.id).toLowerCase().includes(q)
    );
  };

  const renderCmd = () => {
    const rows = matches(cmdQ.value);
    cmdCursor = Math.min(cmdCursor, Math.max(rows.length - 1, 0));
    if (!rows.length) {
      cmdList.innerHTML = `<li class="cmd-empty">No build matches.</li>`;
      return;
    }
    cmdList.innerHTML = rows
      .map(
        (item, i) => `
        <li>
          <a href="${item.href}" aria-selected="${i === cmdCursor}">
            <span class="row-id">${item.id}</span>
            <span>
              <strong>${item.name}</strong>
              <span class="row-line"> · ${item.line}</span>
            </span>
          </a>
        </li>`
      )
      .join("");
  };

  const openCmd = () => {
    cmd.showModal();
    cmdCursor = 0;
    cmdQ.value = "";
    renderCmd();
    cmdQ.focus();
  };

  const closeCmd = () => {
    if (cmd.open) cmd.close();
  };

  const openHelp = () => {
    help.hidden = false;
  };

  const closeHelp = () => {
    help.hidden = true;
  };

  document.querySelectorAll("[data-open-cmd]").forEach((btn) => {
    btn.addEventListener("click", openCmd);
  });
  document.querySelector("[data-close-help]")?.addEventListener("click", closeHelp);
  help.addEventListener("click", (e) => {
    if (e.target === help) closeHelp();
  });

  cmd.addEventListener("close", () => {
    cmdQ.value = "";
  });

  cmdQ.addEventListener("input", () => {
    cmdCursor = 0;
    renderCmd();
  });

  cmd.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (link) closeCmd();
  });

  document.addEventListener("keydown", (e) => {
    const typing =
      e.target instanceof HTMLInputElement ||
      e.target instanceof HTMLTextAreaElement;

    if (e.key === "Escape") {
      closeCmd();
      closeHelp();
      return;
    }

    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      cmd.open ? closeCmd() : openCmd();
      return;
    }

    if (cmd.open) {
      const rows = matches(cmdQ.value);
      if (e.key === "ArrowDown") {
        e.preventDefault();
        cmdCursor = Math.min(cmdCursor + 1, rows.length - 1);
        renderCmd();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        cmdCursor = Math.max(cmdCursor - 1, 0);
        renderCmd();
      } else if (e.key === "Enter") {
        e.preventDefault();
        const pick = rows[cmdCursor];
        if (pick) window.location.assign(pick.href);
      }
      return;
    }

    if (typing) return;

    if (e.key === "?" || (e.shiftKey && e.key === "/")) {
      e.preventDefault();
      help.hidden ? openHelp() : closeHelp();
      return;
    }

    if (e.key === "j") setActive(index + 1);
    if (e.key === "k") setActive(index - 1);
    if (e.key === "Enter") openActive();

    if (e.key === "g") {
      if (gPending) {
        window.scrollTo({ top: 0, behavior: "smooth" });
        gPending = false;
      } else {
        gPending = true;
        setTimeout(() => {
          gPending = false;
        }, 400);
      }
    }
  });

  const tickClock = () => {
    const time = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/New_York",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date());
    document.querySelectorAll("[data-clock]").forEach((el) => {
      el.textContent = `NY · ${time}`;
    });
  };
  tickClock();
  setInterval(tickClock, 15000);

  items.forEach((el, i) => {
    el.addEventListener("focus", () => setActive(i));
    el.addEventListener("mouseenter", () => {
      items.forEach((node) => node.classList.remove("is-active"));
      el.classList.add("is-active");
      index = i;
    });
  });
})();
