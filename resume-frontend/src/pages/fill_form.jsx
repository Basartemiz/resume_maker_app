import React, { useEffect, useMemo, useRef, useState } from "react";
import nunjucks from "nunjucks";
import userData from "/src/media/user.json";
import SidebarLayout from "../components/sidebar";
import StudioSplitPane from "../components/Studio";
import ResumeLocalEditor from "../components/local_editor";
import "./fill_form.css";

/* Build-time (Vite) */
const htmlFiles = import.meta.glob("/src/templates/**/*.html", { as: "raw", eager: true });
const cssFiles  = import.meta.glob("/src/templates/**/*.css",  { as: "raw", eager: true });

const LS_DATA  = "resume_json_v1";
const LS_ORDER = "resume_section_order_v1";

function baseName(p) {
  return p.split("/").pop().replace(/\.[^.]+$/, "");
}

function buildTemplates() {
  const cssByBase = {};
  for (const p in cssFiles) cssByBase[baseName(p)] = { path: p, css: cssFiles[p] };
  const out = [];
  for (const p in htmlFiles) {
    const key = baseName(p);
    out.push({ key, pathHtml: p, html: htmlFiles[p], css: cssByBase[key]?.css || "" });
  }
  return out.sort((a, b) => a.key.localeCompare(b.key));
}

const templatesList = buildTemplates();

function safeParse(json) {
  try { return JSON.parse(json); } catch { return null; }
}

export default function TemplateStudio() {
  const [selectedKey, setSelectedKey] = useState(templatesList[0]?.key || null);
  const iframeRef = useRef(null);

  // Load JSON data (resume info)
  const [data, setData] = useState(() => {
    const fromLS = safeParse(localStorage.getItem(LS_DATA));
    return fromLS ?? userData;
  });

  // Load order list
  const [order, setOrder] = useState(() =>
    JSON.parse(localStorage.getItem(LS_ORDER)) || [
      "profile",
      "skills",
      "education",
      "experience",
      "custom:0",
      "custom:1",
      "custom:2",
      "references",
    ]
  );

  // Small feedback after pressing Save & Apply
  const [appliedMsg, setAppliedMsg] = useState("");

  const ctx = useMemo(() => ({ ...data, order }), [data, order]);

  const selected = useMemo(
    () => templatesList.find((t) => t.key === selectedKey) || null,
    [selectedKey]
  );

  // Configure nunjucks once
  useEffect(() => {
    nunjucks.configure({ autoescape: true });
  }, []);

  // Watch for changes in localStorage (both data + order)
  useEffect(() => {
    let prevData = localStorage.getItem(LS_DATA);
    let prevOrder = localStorage.getItem(LS_ORDER);

    const checkLocalStorage = () => {
      const newData = localStorage.getItem(LS_DATA);
      const newOrder = localStorage.getItem(LS_ORDER);

      if (newData !== prevData) {
        prevData = newData;
        const parsed = safeParse(newData);
        setData(parsed ?? userData);
      }

      if (newOrder !== prevOrder) {
        prevOrder = newOrder;
        const parsedOrder = safeParse(newOrder);
        setOrder(
          parsedOrder ?? [
            "profile",
            "skills",
            "education",
            "experience",
            "custom:0",
            "custom:1",
            "custom:2",
            "references",
          ]
        );
      }
    };

    const id = setInterval(checkLocalStorage, 300);
    const onStorage = (e) => {
      if (e.key === LS_DATA || e.key === LS_ORDER) checkLocalStorage();
    };

    window.addEventListener("storage", onStorage);
    return () => {
      clearInterval(id);
      window.removeEventListener("storage", onStorage);
    };
  }, []);

  // Render template into iframe
  useEffect(() => {
    if (!selected || !iframeRef.current) return;

    let htmlContent = "";
    try {
      htmlContent = nunjucks.renderString(selected.html, ctx);
    } catch (e) {
      htmlContent = `<pre style="color:#b91c1c;background:#fee2e2;padding:12px;border-radius:8px;">Render error: ${String(e)}</pre>`;
    }

    const doc = iframeRef.current.contentDocument;
    if (!doc) return;
    const full = `
<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>${selected.key}</title>
${selected.css ? `<style id="template-css">${selected.css}</style>` : ""}
<style>html,body{height:100%}body{margin:0;background:#fff}</style>
</head><body>${htmlContent}</body></html>`;
    doc.open(); doc.write(full); doc.close();
  }, [selected, ctx]);


  // Put this helper above the component (or inside it before usage)
function normalizeOrder(latestData, latestOrder) {
  const coreKeys = ["profile", "skills", "education", "experience", "references"];
  const customsCount = Array.isArray(latestData?.custom_sections)
    ? latestData.custom_sections.length
    : 0;

  const isCustomKey = (k) => /^custom:\d+$/.test(k);
  const toInt = (s) => {
    const n = Number(s);
    return Number.isFinite(n) ? n : -1;
  };

  // 1) Start from user-provided order (if any)
  const src = Array.isArray(latestOrder) ? latestOrder.slice() : [];

  // 2) Filter to allowed keys only (core + valid custom)
  const filtered = src.filter((k) => {
    if (coreKeys.includes(k)) return true;
    if (isCustomKey(k)) {
      const idx = toInt(k.split(":")[1]);
      return idx >= 0 && idx < customsCount;
    }
    return false;
  });

  // 3) Deduplicate while preserving first occurrence
  const seen = new Set();
  const unique = filtered.filter((k) => (seen.has(k) ? false : (seen.add(k), true)));

  // 4) Append any missing core keys (preserve canonical core order)
  for (const ck of coreKeys) {
    if (!unique.includes(ck)) unique.push(ck);
  }

  // 5) Append any missing custom keys in sequence custom:0..N-1
  for (let i = 0; i < customsCount; i++) {
    const key = `custom:${i}`;
    if (!unique.includes(key)) unique.push(key);
  }

  return unique;
}


  // ------- NEW: Save & Apply handler -------
const handleSaveAndApply = () => {
  // Load latest from localStorage (editor already writes there)
  const latestData  = safeParse(localStorage.getItem(LS_DATA))  ?? userData;
  const latestOrderRaw = safeParse(localStorage.getItem(LS_ORDER)) ?? [
    "profile", "skills", "education", "experience", "references"
  ];

  // Normalize with respect to *current* custom_sections
  const normalizedOrder = normalizeOrder(latestData, latestOrderRaw);

  // Persist normalized order so everything stays in sync
  localStorage.setItem(LS_ORDER, JSON.stringify(normalizedOrder));

  // Update state -> re-renders iframe immediately via ctx
  setData(latestData);
  setOrder(normalizedOrder);

  // Tiny success ping
  setAppliedMsg("Applied ✓");
  window.setTimeout(() => setAppliedMsg(""), 1000);
};


  const navItems = templatesList.map((t) => ({ key: t.key, label: t.key }));

  return (
    <div className="max-h-screen w-full h-full overflow-hidden bg-slate-100 dark:bg-slate-900">
      <SidebarLayout
        items={navItems}
        selectedKey={selectedKey}
        onSelect={setSelectedKey}
        header="Templates"
      >
        {/* Toolbar above the split pane */}
        <div className="d-flex align-items-center justify-content-end gap-2 mb-2">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={handleSaveAndApply}
            title="Save data and re-render the selected template"
          >
            Save & Apply
          </button>
          {appliedMsg && <span className="small text-success">{appliedMsg}</span>}
        </div>

        <StudioSplitPane
          iframeRef={iframeRef}
          EditorComponent={ResumeLocalEditor}
          editorTitle="Resume Editor"
        />
      </SidebarLayout>
    </div>
  );
}
