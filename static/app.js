
const API_BASE = "";

const resources = {
  students: {
    endpoint: "/students",
    title: "Students",
    subtitle: "Student records from your database",
    icon: "♙",
    columns: [
      ["Student number", ["student_number", "student_id"]],
      ["First name", ["first_name"]],
      ["Last name", ["last_name"]],
      ["Grade", ["grade_level", "grade"]],
      ["ID", ["id"]],
    ],
  },
  buses: {
    endpoint: "/buses",
    title: "Buses",
    subtitle: "Registered school buses",
    icon: "▰",
    columns: [
      ["Bus number", ["bus_number", "number"]],
      ["Capacity", ["capacity"]],
      ["Status", ["status", "is_active"]],
      ["ID", ["id"]],
    ],
  },
  routes: {
    endpoint: "/routes",
    title: "Routes",
    subtitle: "Configured transportation routes",
    icon: "⇄",
    columns: [
      ["Route name", ["name", "route_name"]],
      ["Direction", ["direction"]],
      ["School arrival", ["scheduled_school_arrival"]],
      ["ID", ["id"]],
    ],
  },
  trips: {
    endpoint: "/trips",
    title: "Trips",
    subtitle: "Recorded bus trips",
    icon: "◷",
    columns: [
      ["Service date", ["service_date", "date"]],
      ["Status", ["status"]],
      ["Route ID", ["route_id"]],
      ["Bus ID", ["bus_id"]],
      ["ID", ["id"]],
    ],
  },
  attendance: {
    endpoint: "/attendance",
    title: "Attendance",
    subtitle: "Attendance records saved in the backend",
    icon: "✓",
    columns: [
      ["Student ID", ["student_id"]],
      ["Trip ID", ["trip_id"]],
      ["Status", ["status"]],
      ["Recorded at", ["recorded_at", "created_at"]],
      ["Note", ["note"]],
    ],
  },
};

const state = {
  students: [],
  buses: [],
  routes: [],
  trips: [],
  attendance: [],
  page: "overview",
  loading: false,
};

const $ = (selector) => document.querySelector(selector);

function textValue(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function getValue(record, candidates) {
  for (const key of candidates) {
    if (record && record[key] !== undefined && record[key] !== null) {
      return record[key];
    }
  }

  return "—";
}

function normalizeRecords(payload) {
  // Support common response shapes: an array, or an object
  // containing a list under a familiar property.
  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && typeof payload === "object") {
    for (const key of ["items", "results", "records", "data"]) {
      if (Array.isArray(payload[key])) {
        return payload[key];
      }
    }
  }

  throw new Error(
    "The API response wasn't a list of records. Check the endpoint response in /docs."
  );
}

async function fetchRecords(resource) {
  const response = await fetch(API_BASE + resource.endpoint, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(
      `${resource.endpoint} returned HTTP ${response.status}`
    );
  }

  const payload = await response.json();
  return normalizeRecords(payload);
}

function setConnection(connected, message) {
  const dot = $("#connection-dot");
  dot.classList.toggle("online", connected);
  dot.classList.toggle("offline", !connected);

  $("#connection-label").textContent = message;
  $("#status-title").textContent = connected
    ? "Backend connected"
    : "Backend connection needs attention";

  $("#status-description").textContent = connected
    ? "BusSync successfully retrieved data from your local API."
    : "Check the server and the error message above.";
}

function showError(message) {
  $("#error-panel").hidden = false;
  $("#error-message").textContent = message;
}

function clearError() {
  $("#error-panel").hidden = true;
  $("#error-message").textContent = "";
}

function setText(selector, value) {
  $(selector).textContent = textValue(value);
}

function makeElement(tag, className, value) {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  if (value !== undefined) {
    element.textContent = textValue(value);
  }

  return element;
}

function renderPreview(containerSelector, records, resourceName, limit = 3) {
  const container = $(containerSelector);
  container.replaceChildren();

  if (!records.length) {
    container.append(
      makeElement("p", "muted", "No records found yet.")
    );
    return;
  }

  records.slice(0, limit).forEach((record) => {
    const resource = resources[resourceName];
    const item = makeElement("div", "preview-item");
    const icon = makeElement("div", "preview-icon", resource.icon);
    const info = makeElement("div", "preview-info");

    let title = "Record";
    let detail = `ID: ${textValue(record.id)}`;

    if (resourceName === "buses") {
      title = `Bus ${textValue(record.bus_number ?? record.id)}`;
      detail = `Capacity: ${textValue(record.capacity)}`;
    } else if (resourceName === "trips") {
      title = textValue(record.service_date ?? record.id);
      detail = `Status: ${textValue(record.status)}`;
    }

    info.append(
      makeElement("strong", "", title),
      makeElement("small", "", detail)
    );

    item.append(icon, info);

    if (record.status !== undefined) {
      item.append(makeElement("span", "preview-badge", record.status));
    }

    container.append(item);
  });
}

function renderTable(page) {
  const resource = resources[page];
  const records = state[page];

  $("#records-title").textContent = resource.title;
  $("#records-subtitle").textContent = resource.subtitle;
  $("#record-count").textContent =
    `${records.length} record${records.length === 1 ? "" : "s"}`;

  const head = $("#table-head");
  const body = $("#table-body");

  head.replaceChildren();
  body.replaceChildren();

  const headerRow = document.createElement("tr");

  resource.columns.forEach(([label]) => {
    headerRow.append(makeElement("th", "", label));
  });

  head.append(headerRow);

  if (!records.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = resource.columns.length;
    cell.textContent = "No records found.";
    cell.className = "muted";

    row.append(cell);
    body.append(row);
    return;
  }

  records.forEach((record) => {
    const row = document.createElement("tr");

    resource.columns.forEach(([, keys]) => {
      const cell = document.createElement("td");
      const value = getValue(record, keys);

      if (keys.includes("recorded_at") || keys.includes("created_at")) {
        cell.textContent =
          value === "—" ? value : formatDate(value);
      } else {
        cell.textContent = textValue(value);
      }

      row.append(cell);
    });

    body.append(row);
  });
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return textValue(value);
  }

  return date.toLocaleString();
}

function renderOverview() {
  setText("#student-count", state.students.length);
  setText("#bus-count", state.buses.length);
  setText("#route-count", state.routes.length);
  setText("#trip-count", state.trips.length);

  renderPreview("#fleet-preview", state.buses, "buses");
  renderPreview("#trip-preview", state.trips, "trips");
}

function showPage(page) {
  state.page = page;

  document.querySelectorAll(".nav-item").forEach((button) => {
    const active = button.dataset.page === page;
    button.classList.toggle("active", active);
    button.setAttribute("aria-current", active ? "page" : "false");
  });

  const overview = page === "overview";
  $("#overview-page").hidden = !overview;
  $("#records-page").hidden = overview;

  const titles = {
    overview: "Overview",
    ...Object.fromEntries(
      Object.entries(resources).map(([key, resource]) => [
        key,
        resource.title,
      ])
    ),
  };

  $("#page-title").textContent = titles[page] || "Overview";

  if (!overview && resources[page]) {
    renderTable(page);
  }
}

async function loadDashboard() {
  if (state.loading) return;

  state.loading = true;
  $("#refresh-button").disabled = true;
  $("#refresh-button").style.opacity = "0.7";

  try {
    const entries = Object.entries(resources);

    // Load all five resources. The backend must be running.
    const results = await Promise.all(
      entries.map(([, resource]) => fetchRecords(resource))
    );

    entries.forEach(([key], index) => {
      state[key] = results[index];
    });

    renderOverview();
    clearError();
    setConnection(true, "Connected");
    showPage(state.page);
  } catch (error) {
    setConnection(false, "Disconnected");

    showError(
      error instanceof Error
        ? error.message
        : "An unexpected error occurred."
    );
  } finally {
    state.loading = false;
    $("#refresh-button").disabled = false;
    $("#refresh-button").style.opacity = "1";
  }
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    showPage(button.dataset.page);
  });
});

document.querySelectorAll("[data-go]").forEach((button) => {
  button.addEventListener("click", () => {
    showPage(button.dataset.go);
  });
});

$("#refresh-button").addEventListener("click", loadDashboard);

$("#current-date").textContent = new Date().toLocaleDateString(
  undefined,
  { weekday: "short", month: "short", day: "numeric", year: "numeric" }
);

showPage("overview");
loadDashboard();
