import React, { useEffect, useMemo, useState } from "react";
import ResumeLocalEditor from "./local_editor"; // ← your local-only editor
import "./studio.css";

export default function StudioSplitPane({
  iframeRef,
  modeStorageKey = "studio_view_mode",
  initialMode = "editor", // "editor" | "preview"
  EditorComponent = ResumeLocalEditor,
  editorTitle = "Resume Editor",
})  {
  useEffect(() => {
    // Ensure the mode key is initialized (useful for first load / storage-disabled cases).
    try {
      const existing = localStorage.getItem(modeStorageKey);
      if (!existing) localStorage.setItem(modeStorageKey, initialMode);
    } catch {
      return;
    }
  }, [initialMode, modeStorageKey]);

  const [mode, setMode] = useState(() => {
    try {
      const saved = localStorage.getItem(modeStorageKey);
      return saved === "preview" || saved === "editor" ? saved : initialMode;
    } catch {
      return initialMode;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(modeStorageKey, mode);
    } catch {
      return;
    }
  }, [mode, modeStorageKey]);

  const openPreviewInNewTab = () => {
    const doc = iframeRef?.current?.contentDocument;
    if (!doc) return;
    const blob = new Blob([doc.documentElement.outerHTML], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener,noreferrer");
    window.setTimeout(() => URL.revokeObjectURL(url), 10_000);
  };

  const modeLabel = useMemo(
    () => (mode === "editor" ? "Editor" : "Preview"),
    [mode]
  );

  return (
    <div className="studio-shell px-3 py-3">
      {/* Top-toolbar */}
      <div className="studio-toolbar d-flex align-items-center justify-content-between gap-3 mb-3">
        <div className="d-flex align-items-center gap-2 min-w-0">
          <span className="studio-chip" title="Local-only (auto-saved)">Local</span>
          <div className="min-w-0">
            <div className="studio-title text-truncate">{editorTitle}</div>
            <div className="studio-subtitle text-truncate">Switch between editing and preview</div>
          </div>
        </div>

        <div className="d-flex align-items-center gap-2 flex-wrap justify-content-end">
          <div className="studio-segment" role="tablist" aria-label="View mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "editor"}
              className={`studio-segment-btn ${mode === "editor" ? "is-active" : ""}`}
              onClick={() => setMode("editor")}
            >
              Editor
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === "preview"}
              className={`studio-segment-btn ${mode === "preview" ? "is-active" : ""}`}
              onClick={() => setMode("preview")}
            >
              Preview
            </button>
          </div>

          <button
            type="button"
            className="btn btn-outline-secondary btn-sm studio-open-btn"
            onClick={openPreviewInNewTab}
            title="Open preview in a new tab"
          >
            Open
          </button>
        </div>
      </div>

      {/* Single-pane stage (both panes stay mounted; we just toggle visibility) */}
      <div
        className="studio-stage rounded-4 border bg-body-tertiary"
        style={{ height: "calc(100vh - 170px)" }}
        data-mode={mode}
        aria-label={`Studio ${modeLabel}`}
      >
        <section
          className={`studio-pane ${mode === "editor" ? "is-active" : ""}`}
          aria-hidden={mode !== "editor"}
        >
          <div className="card studio-card shadow-sm border-0 h-100">
            <div className="card-header bg-white d-flex align-items-center justify-content-between">
              <strong>Editor</strong>
              <span className="text-muted small">Autosaves to localStorage</span>
            </div>
            <div className="card-body overflow-auto">
              {React.createElement(EditorComponent, { title: editorTitle })}
            </div>
          </div>
        </section>

        <section
          className={`studio-pane ${mode === "preview" ? "is-active" : ""}`}
          aria-hidden={mode !== "preview"}
        >
          <div className="card studio-card shadow-sm border-0 h-100">
            <div className="card-header bg-white d-flex align-items-center justify-content-between">
              <strong>Template Preview</strong>
              <span className="text-muted small">Live</span>
            </div>
            <div className="card-body p-0">
              <iframe
                ref={iframeRef}
                title="Template Preview"
                sandbox="allow-scripts allow-same-origin"
                className="w-100 h-100"
                style={{ border: 0, borderRadius: "0 0 .5rem .5rem" }}
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
