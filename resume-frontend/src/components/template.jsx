// SidebarItem.jsx
import React, { forwardRef } from "react";
import "./template.css";
/**
 * SidebarItem (Bootstrap)
 * - Uses list-group + utilities (no custom CSS required)
 * - Variants: "soft" | "solid" | "ghost"  → mapped to Bootstrap styles
 * - Sizes: "sm" | "md" | "lg"
 * - Collapsed hides label/subtitle/badge (keeps icon)
 * - Renders <a> if href is given, else <button>
 */
const SidebarItem = forwardRef(
  (
    {
      label,
      subtitle,
      icon,
      badge,
      active = false,
      collapsed = false,
      loading = false,
      disabled = false,
      size = "md",              // "sm" | "md" | "lg"
      variant = "soft",         // "soft" | "solid" | "ghost"
      className = "",
      title,
      href,
      target,
      rel,
      onClick,
      rightSlot,
      badgeAriaLabel,
      "aria-current": ariaCurrent,
      ...rest
    },
    ref
  ) => {
    const Comp = href ? "a" : "button";
    const computedTitle = collapsed ? (title || label) : title;

    // Size → spacing & font utilities
    const sizeCls =
      size === "sm"
        ? "py-1 px-2 small"
        : size === "lg"
        ? "py-3 px-3 fs-6"
        : "py-2 px-2"; // md

    // Variant → Bootstrap-friendly styles
    // (We style like a clickable list item using list-group + subtle backgrounds)
    const variantCls = (() => {
      if (variant === "solid") return active ? "active" : "bg-body-secondary";
      if (variant === "ghost") return active ? "active" : "bg-transparent";
      // soft (default)
      return active ? "active" : "bg-body-tertiary";
    })();

    // Disabled/active helpers
    const stateCls = [
      "list-group-item",
      "list-group-item-action",
      "border-0",
      "rounded-2",
      "d-flex",
      "align-items-center",
      "gap-2",
      "w-100",
      variantCls,
      sizeCls,
      disabled ? "disabled" : "",
      className,
    ]
      .join(" ")
      .replace(/\s+/g, " ")
      .trim();

    // a11y
    const ariaProps = {
      "aria-current": active ? ariaCurrent || "page" : undefined,
      "aria-disabled": disabled || undefined,
      "aria-busy": loading || undefined,
      title: computedTitle,
    };

    return (
      <li className="list-group-item p-0 bg-transparent border-0">
        <Comp
          ref={ref}
          className={stateCls}
          type={href ? undefined : "button"}
          href={href}
          target={href ? target : undefined}
          rel={href && target === "_blank" ? rel || "noopener noreferrer" : rel}
          onClick={disabled ? undefined : onClick}
          tabIndex={disabled ? -1 : 0}
          {...ariaProps}
          {...rest}
        >
          {/* Icon / Initial */}
          <span
            className="d-inline-flex justify-content-center align-items-center rounded-2"
            style={{ width: 28, height: 28 }}
            aria-hidden={!!icon ? undefined : true}
          >
            {icon ?? (
              <span className="fw-semibold">
                {(label || "?").trim().charAt(0).toUpperCase()}
              </span>
            )}
          </span>

          {/* Text (hidden when collapsed) */}
          {!collapsed && (
            <span className="d-flex flex-column text-start flex-grow-1 min-w-0">
              <span className="fw-semibold text-truncate" title={label}>
                {label}
              </span>
              {subtitle && (
                <small className={`text-secondary text-truncate`}>
                  {subtitle}
                </small>
              )}
            </span>
          )}

          {/* Badge (hidden when collapsed) */}
          {!collapsed && badge !== undefined && (
            <span
              className={`badge ${active ? "text-bg-light" : "text-bg-secondary"} ms-auto`}
              aria-label={badgeAriaLabel}
              title={badgeAriaLabel || String(badge)}
            >
              {badge}
            </span>
          )}

          {/* Right slot (chevron, shortcut, etc.) */}
          {!collapsed && rightSlot && (
            <span className="ms-1" aria-hidden="true">
              {rightSlot}
            </span>
          )}

          {/* Loading spinner (non-blocking) */}
          {loading && (
            <span
              className="spinner-border spinner-border-sm ms-2"
              role="status"
              aria-hidden="true"
            />
          )}
        </Comp>
      </li>
    );
  }
);

export default SidebarItem;
