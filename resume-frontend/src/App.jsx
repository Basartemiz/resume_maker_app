import { Routes, Route, Link } from "react-router-dom";
import Enterence from "./pages/enterence.jsx";
import TemplateStudio from "./pages/fill_form.jsx";
import "./App.css";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Simple top bar navigation */}
      
      {/* Page outlet */}
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Enterence />} />
          <Route path="/fill" element={<TemplateStudio />} />
        </Routes>
      </main>

    </div>
  );
}
