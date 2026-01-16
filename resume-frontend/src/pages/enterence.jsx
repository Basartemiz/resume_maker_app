import React, { useEffect, useMemo, useRef, useState } from "react";
import micIcon from "../assets/mic.png"; // your microphone image
import { useNavigate } from "react-router-dom";
import "./entrence.css";

export default function Enterence({
  placeholder = "Type something…",
  onSubmit,        // optional callback: (value) => void
  maxLength = 160, // live counter
}) {
  const [value, setValue] = useState("");
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const navigate = useNavigate(); // <-- you imported it; now use it

  // Speech recognition (if available)
  const recognition = useMemo(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;
    const r = new SR();
    r.lang = "en-US";
    r.interimResults = true;
    r.continuous = false;
    return r;
  }, []);

  useEffect(() => {
    if (!recognition) return;

    const handleResult = (e) => {
      const transcript = Array.from(e.results)
        .map((res) => res[0].transcript)
        .join(" ");
      setValue((prev) => (prev ? `${prev} ${transcript}` : transcript));
    };

    const handleEnd = () => setListening(false);
    const handleError = (e) => {
      setListening(false);
      setError(e.error || "Microphone error");
      setTimeout(() => setError(""), 2000);
    };

    recognition.addEventListener("result", handleResult);
    recognition.addEventListener("end", handleEnd);
    recognition.addEventListener("error", handleError);

    return () => {
      recognition.removeEventListener("result", handleResult);
      recognition.removeEventListener("end", handleEnd);
      recognition.removeEventListener("error", handleError);
    };
  }, [recognition]);

  const toggleMic = () => {
    if (!recognition) {
      alert("Microphone clicked! (SpeechRecognition not supported)");
      return;
    }
    if (listening) {
      recognition.stop();
      setListening(false);
    } else {
      setError("");
      setListening(true);
      recognition.start();
    }
  };

  const doSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed) {
      setError("Please enter something");
      setTimeout(() => setError(""), 1500);
      return;
    }
    localStorage.setItem("userInput", trimmed);
    if (onSubmit) onSubmit(trimmed);
    navigate("/fill");
    setValue("");
  };

  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") setValue("");
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const remaining = maxLength - value.length;
  const overLimit = remaining < 0;

  return (
    <div className="min-vh-100 w-100 page-gradient d-flex flex-column align-items-center justify-content-center">
      {/* Headings */}
      <div className="container py-4">
        <h1 className="display-5 fw-bold text-center mb-2 gradient-text">
          Your CV is ready in under one minute
        </h1>
        <p className="lead text-center text-muted">
          Get started by filling out the form below:
        </p>
      </div>

      {/* Card */}
      <div className="container mb-4">
        <div className="card shadow-sm border-0">
          <div className="card-body">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                doSubmit();
              }}
              aria-label="Text input with microphone"
              className="d-flex flex-column gap-3"
            >
              {/* Textarea with clear button */}
              <div className="position-relative">
                <textarea
                  ref={inputRef}
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  placeholder={placeholder || "Write about yourself..."}
                  maxLength={maxLength + 100} // allow slight overflow but flag it
                  rows={5}
                  className={`form-control ${overLimit ? "is-invalid" : ""}`}
                  aria-invalid={overLimit || !!error}
                  aria-describedby="helper-text"
                />
                {value && (
                  <button
                    type="button"
                    onClick={() => setValue("")}
                    className="clear-btn"
                    aria-label="Clear text"
                    title="Clear"
                  >
                    {/* Bootstrap close icon */}
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                )}
                {overLimit && (
                  <div className="invalid-feedback">
                    You’ve exceeded the recommended character limit.
                  </div>
                )}
              </div>

              {/* Row with mic + submit */}
              <div className="d-flex align-items-center gap-2">
                <button
                  type="button"
                  onClick={toggleMic}
                  className={`btn btn-outline-primary btn-mic ${listening ? "listening" : ""}`}
                  aria-pressed={listening}
                  aria-label={listening ? "Stop recording" : "Start recording"}
                  title={listening ? "Stop recording" : "Start recording"}
                >
                  {listening ? (
                    <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                  ) : (
                    <img src={micIcon} alt="Microphone" className="img-fluid" style={{ width: 20, height: 20 }} />
                  )}
                </button>

                <button
                    type="submit"
                    className="btn btn-gradient px-4 py-2 fw-semibold d-inline-flex align-items-center justify-content-center gap-2"
                    >
                    <span>Send</span>
                    <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                        className="ms-0"
                    >
                        <path
                        fill="currentColor"
                        d="M2.01 21L23 12L2.01 3L2 10l15 2l-15 2z"
                        />
                    </svg>
                    </button>

                {/* Spacer grows to push counter right on larger screens */}
                <div className="flex-grow-1" />
                {/* Counter */}
                <span
                  className={`badge ${overLimit ? "text-bg-danger" : "text-bg-secondary"}`}
                  title="Remaining characters"
                >
                  {remaining} / {maxLength}
                </span>
              </div>

              {/* Helper + Error */}
              <div id="helper-text" className="d-flex justify-content-between text-muted small">
                <div>
                  Press <kbd>Enter</kbd> to submit, <kbd>Esc</kbd> to clear. Focus: <kbd>⌘/Ctrl + K</kbd>
                </div>
              </div>

              {error && (
                <div className="alert alert-danger py-2 mb-0" role="alert">
                  {error}
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Footer tip */}
        <div className="mt-4 text-center">
          <p className="text-secondary m-0">
            💡 Include your <strong className="text-primary">name</strong>, <strong>email</strong>, and a short
            <strong> message</strong> about yourself to enhance your resume creation.
          </p>
        </div>
      </div>
    </div>
  );
}
