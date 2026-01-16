import React, { useEffect, useMemo, useRef, useState } from "react";
import SidebarItem from "./template";
import "./sidebar.css";
/**
 * Props
 * - items: [{ key, label, subtitle?, icon? (JSX), badge? (string|number) }]
 * - selectedKey: string
 * - onSelect: (key) => void
 * - header: string
 * - sidebarWidth: number (px)
 * - collapsedWidth: number (px)  // still supported if you want a collapsed mode

 * - persistenceKey: string (localStorage key)
 */
export default function SidebarLayout({
  items = [],
  selectedKey,
  onSelect,
  header = "Templates",
  sidebarWidth = 260,
  collapsedWidth = 76,
  persistenceKey = "sidebar-state",
  children,
}) {
  const [open, setOpen] = useState(false);           // mobile drawer
  const [collapsed, setCollapsed] = useState(false); // desktop collapsed (icon-only)
  const [showSidebar, setShowSidebar] = useState(true); // NEW: desktop visibility
  const [q, setQ] = useState("");
  const firstFocusRef = useRef(null);

  // Load persisted state
  useEffect(() => {
    try {
      const raw = localStorage.getItem(persistenceKey);
      if (raw) {
        const { collapsed: c, showSidebar: s } = JSON.parse(raw);
        if (typeof c === "boolean") setCollapsed(c);
        if (typeof s === "boolean") setShowSidebar(s);
      }
    } catch {}
  }, [persistenceKey]);

  // Persist state
  useEffect(() => {
    try {
      localStorage.setItem(
        persistenceKey,
        JSON.stringify({ collapsed, showSidebar })
      );
    } catch {}
  }, [collapsed, showSidebar, persistenceKey]);

  // Filtered nav items
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return items;
    return items.filter((it) =>
      `${it.label} ${it.subtitle || ""}`.toLowerCase().includes(needle)
    );
  }, [items, q]);

  // Close on ESC (mobile drawer)
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  // Body scroll lock + focus when opening on mobile
  useEffect(() => {
    if (open) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      setTimeout(() => firstFocusRef.current?.focus(), 0);
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [open]);

  // Width styles
  const currentWidth = collapsed ? collapsedWidth : sidebarWidth;

  // If the sidebar is fully hidden on desktop, main should occupy full width.
  const mainStyle = {
    marginLeft: showSidebar ? currentWidth : 0,
    transition: "margin-left .25s ease",
  };

  const sidebarStyle = {
    width: `${currentWidth}px`,
    zIndex: 1040,
    transition: "width .25s ease, transform .25s ease",
    boxSizing: "border-box",
  };

  // Helpers
  const isCollapsed = collapsed && !open; // collapsed applies to desktop (lg+) only
  const renderIconOrInitial = (icon, label) => {
    if (icon) return icon;
    const initial = (label || "?").trim().charAt(0).toUpperCase();
    return (
      <span
        className="d-inline-flex align-items-center justify-content-center rounded-circle bg-secondary text-white"
        style={{ width: 28, height: 28, fontSize: 13 }}
      >
        {initial}
      </span>
    );
  };

  return (
    <div className="d-flex vh-100 bg-light position-relative overflow-hidden">
      {/* Sidebar — render only if mobile drawer is open OR desktop showSidebar */}
      {(open || showSidebar) && (
        <nav
          role="navigation"
          aria-label={`${header} navigation`}
          className={`sidebar-glass position-fixed top-0 start-0 h-100 p-3 overflow-auto border-0 shadow-lg ${
            open ? "d-block" : "d-none d-lg-block"
          } ${isCollapsed ? "sidebar-collapsed" : ""}`}
          style={sidebarStyle}
        >
          {/* Brand / Header row */}
          <div className="d-flex align-items-center justify-content-between mb-3 brand-bar rounded-4 px-3 py-2">
            <div className="d-flex align-items-center gap-2">
              <span className="brand-dot rounded-circle"></span>
              <h6
                className="m-0 text-white fw-semibold text-truncate"
                title={header}
              >
                {header}
              </h6>
            </div>

            {/* Close (mobile) */}
            <button
              className="btn btn-outline-light btn-sm d-lg-none"
              onClick={() => setOpen(false)}
              aria-label="Close menu"
              ref={firstFocusRef}
            >
              ✕
            </button>

            {/* Collapse/Expand (desktop) */}
            {!open && (
              <div className="d-none d-lg-inline-flex gap-1">
              
                {/* NEW: Hide/Show toggle for desktop */}
                <button
                  className="btn btn-outline-light btn-sm"
                  onClick={() => setShowSidebar(false)}
                  aria-label="Hide sidebar"
                  title="Hide"
                >
                  ✕
                </button>
              </div>
            )}
          </div>

          
          

          {/* Nav list */}
          <aside className="sidebar-classic">
            <ul className="sidebar-classic nav flex-column mt-2 bg-dark text-white rounded-3 p-2">
              {filtered.map(({ key, label, subtitle, icon, badge }) => {
                return (
                  <SidebarItem
                    label="harvard"
                    subtitle="Template"
                    active={key === selectedKey}
                    key={key}
                    icon={renderIconOrInitial(icon, label)}
                    badge={badge}
                  ref={key === filtered[0].key ? firstFocusRef : null}
                  tabIndex={0}
                  
                  onClick={() => {
                    onSelect(key);
                    setOpen(false);
                  }}
                  />
              );
            })}


            {filtered.length === 0 && !isCollapsed && (
              <li className="nav-item">
                <span className="text-muted small">No matches.</span>
              </li>
            )}
          </ul>
          </aside>

          {/* Footer actions (hide in collapsed) */}
          
        </nav>
      )}

      {/* Overlay for mobile */}
      {open && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-lg-none"
          style={{ zIndex: 1030 }}
          onClick={() => setOpen(false)}
        />
      )}

      {/* Main Content Area */}
      <div className="flex-grow-1 px-3" style={mainStyle}>
        {/* Top Bar */}
        <div className="bg-white border-bottom shadow-sm d-flex align-items-center justify-content-between px-3 py-2 sticky-top">
          <div className="d-flex align-items-center gap-2">
            {/* Mobile: open drawer */}
            <button
              className="btn btn-outline-secondary d-lg-none"
              onClick={() => setOpen(true)}
              aria-label="Open sidebar"
            >
              ☰
            </button>

            {/* Desktop: Show/Hide + Collapse */}
            <div className="d-none d-lg-inline-flex gap-2">
              <button
                className="btn btn-outline-secondary"
                onClick={() => setShowSidebar((v) => !v)}
                aria-label={showSidebar ? "Hide sidebar" : "Show sidebar"}
                title={showSidebar ? "Hide sidebar" : "Show sidebar"}
              >
                {showSidebar ? "Hide" : "Show"}
              </button>
              {showSidebar && (
                <button
                  className="btn btn-outline-secondary"
                  onClick={() => setCollapsed((v) => !v)}
                  aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                  title={collapsed ? "Expand" : "Collapse"}
                >
                  {collapsed ? "Expand" : "Collapse"}
                </button>
              )}
            </div>

            <h6 className="m-0">{header}</h6>
          </div>

          {/* Right side actions placeholder */}
          <div className="d-flex align-items-center gap-2">
            {/* Add any topbar controls here */}
          </div>
        </div>

        {/* Main Content */}
        <main className="h-full w-full container-fluid py-4">{children}</main>
      </div>
    </div>
  );
}
