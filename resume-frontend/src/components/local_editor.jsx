import React, { useEffect, useMemo, useState } from "react";
// Data comes from localStorage (populated by backend API)
import CustomSectionEditorSingle from "./customSectionEditor";
const LS_DATA = "resume_json_v1";
const LS_ORDER = "resume_section_order_v1";

/* ============ Schema & helpers ============ */
const defaultData = () => ({
  name: "",
  title: "",
  contacts: {
    email: "",
    phone: "",
    github: "",
    linkedin: "",
    location: null,
  },
  profile: {
    job_title: "",
    highest_degree: null,
    key_skills: [],
    summary: "",
  },
  skills: {
    sections: [
      {
        label: "Technical",
        items: [],
        note: "",
      },
      {
        label: "Soft",
        items: [],
        note: "",
      },
    ],
  },
  education: [{ education: null, date: null, description: null }],
  experience: [{ position_or_company: null, date: null, description: null }],
  references: [],
  custom_sections: [],
});

// Fallback clone to avoid mutating references
const clone = (x) => JSON.parse(JSON.stringify(x));

// Word count helper - counts all text in the resume
const MAX_WORDS = 10000;

const countWords = (obj) => {
  if (!obj) return 0;
  if (typeof obj === 'string') {
    return obj.trim().split(/\s+/).filter(w => w.length > 0).length;
  }
  if (Array.isArray(obj)) {
    return obj.reduce((sum, item) => sum + countWords(item), 0);
  }
  if (typeof obj === 'object') {
    return Object.values(obj).reduce((sum, val) => sum + countWords(val), 0);
  }
  return 0;
};

const ensureShape = (raw) => {
  // Merge loaded raw into the expected base structure while preserving raw values
  const base = defaultData();
  const out = clone({ ...base, ...raw });
  // merge nested objects carefully
  out.contacts = { ...base.contacts, ...(raw?.contacts || {}) };
  out.profile = { ...base.profile, ...(raw?.profile || {}) };
  out.skills = {
    sections: Array.isArray(raw?.skills?.sections)
      ? clone(raw.skills.sections)
      : clone(base.skills.sections),
  };
  out.education = Array.isArray(raw?.education) ? clone(raw.education) : clone(base.education);
  out.experience = Array.isArray(raw?.experience) ? clone(raw.experience) : clone(base.experience);
  out.references = Array.isArray(raw?.references) ? clone(raw.references) : clone(base.references);
  out.custom_sections = Array.isArray(raw?.custom_sections) ? clone(raw.custom_sections) : [];
  return out;
};

// Default display order (keys or custom:idx)
const defaultOrder = () => [
  "profile",
  "skills",
  "education",
  "experience",
  "references",
  // then each custom section as "custom:0", "custom:1", ...
];

/* ============ Small UI helpers ============ */
const Text = ({ label, value, onChange, placeholder }) => (
  <div className="mb-2">
    <label className="form-label fw-semibold">{label}</label>
    <input
      className="form-control form-control-sm"
      type="text"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

const TextArea = ({ label, value, onChange, rows = 4, placeholder }) => (
  <div className="mb-2">
    <label className="form-label fw-semibold">{label}</label>
    <textarea
      className="form-control form-control-sm"
      rows={rows}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

const Badge = ({ children }) => (
  <span className="badge text-bg-secondary">{children}</span>
);

/* ============ Section Editors ============ */
function ContactsEditor({ data, setData }) {
  const c = data.contacts || {};
  const upd = (k, v) => setData({ ...data, contacts: { ...c, [k]: v || null } });
  return (
    <div>
      <div className="row g-2">
        <div className="col-md-6"><Text label="Email" value={c.email} onChange={(v)=>upd("email",v)} /></div>
        <div className="col-md-6"><Text label="Phone" value={c.phone} onChange={(v)=>upd("phone",v)} /></div>
        <div className="col-md-6"><Text label="GitHub" value={c.github} onChange={(v)=>upd("github",v)} /></div>
        <div className="col-md-6"><Text label="LinkedIn" value={c.linkedin} onChange={(v)=>upd("linkedin",v)} /></div>
        <div className="col-md-12"><Text label="Location" value={c.location} onChange={(v)=>upd("location",v)} /></div>
      </div>
    </div>
  );
}

function ProfileEditor({ data, setData }) {
  const p = data.profile || {};
  const upd = (k, v) => setData({ ...data, profile: { ...p, [k]: v ?? null } });

  const addSkill = () => {
    const arr = Array.isArray(p.key_skills) ? [...p.key_skills] : [];
    arr.push("");
    upd("key_skills", arr);
  };
  const setSkill = (idx, v) => {
    const arr = [...(p.key_skills || [])];
    arr[idx] = v;
    upd("key_skills", arr);
  };
  const rmSkill = (idx) => {
    const arr = [...(p.key_skills || [])];
    arr.splice(idx, 1);
    upd("key_skills", arr);
  };

  return (
    <>
      <div className="row g-2">
        <div className="col-md-6"><Text label="Name" value={data.name} onChange={(v)=>setData({ ...data, name: v })} /></div>
        <div className="col-md-6"><Text label="Title" value={data.title} onChange={(v)=>setData({ ...data, title: v })} /></div>
        <div className="col-md-6"><Text label="Job Title" value={p.job_title} onChange={(v)=>upd("job_title",v)} /></div>
        <div className="col-md-6"><Text label="Highest Degree" value={p.highest_degree} onChange={(v)=>upd("highest_degree",v)} /></div>
      </div>
      <TextArea label="Summary" value={p.summary} onChange={(v)=>upd("summary",v)} rows={5} />

      <div className="mt-2">
        <div className="d-flex align-items-center justify-content-between">
          <label className="form-label fw-semibold m-0">Key Skills</label>
          <button className="btn btn-sm btn-outline-primary" onClick={addSkill}>+ Add</button>
        </div>
        {(p.key_skills || []).map((s, i) => (
          <div key={i} className="d-flex align-items-center gap-2 mb-2">
            <input className="form-control form-control-sm" value={s} onChange={(e)=>setSkill(i,e.target.value)} />
            <button className="btn btn-sm btn-outline-danger" onClick={()=>rmSkill(i)}>Remove</button>
          </div>
        ))}
      </div>
    </>
  );
}

function SkillsEditor({ data, setData }) {
  const sections = data.skills?.sections || [];
  const setSections = (arr) => setData({ ...data, skills: { sections: arr } });

  const addSection = () => setSections([...sections, { label: "", items: [""], note: "" }]);
  const rmSection = (i) => { const arr = [...sections]; arr.splice(i,1); setSections(arr); };
  const move = (i, dir) => {
    const j = i + dir;
    if (j < 0 || j >= sections.length) return;
    const arr = [...sections];
    [arr[i], arr[j]] = [arr[j], arr[i]];
    setSections(arr);
  };

  const setVal = (i, k, v) => {
    const arr = [...sections];
    arr[i] = { ...arr[i], [k]: v };
    setSections(arr);
  };

  const addItem = (i) => setVal(i, "items", [...(sections[i].items || []), ""]);
  const setItem = (i, idx, v) => {
    const items = [...(sections[i].items || [])];
    items[idx] = v;
    setVal(i, "items", items);
  };
  const rmItem = (i, idx) => {
    const items = [...(sections[i].items || [])];
    items.splice(idx,1);
    setVal(i, "items", items);
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-2">
        <h6 className="m-0">Skill Sections</h6>
        <button className="btn btn-sm btn-outline-primary" onClick={addSection}>+ Add Section</button>
      </div>

      {sections.map((sec, i) => (
        <div key={i} className="border rounded-3 p-2 mb-2 bg-white">
          <div className="d-flex align-items-center justify-content-between mb-2">
            <div className="d-flex gap-2">
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i,-1)} title="Move up">↑</button>
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i, 1)} title="Move down">↓</button>
            </div>
            <button className="btn btn-sm btn-outline-danger" onClick={()=>rmSection(i)}>Remove section</button>
          </div>

          <Text label="Label" value={sec.label} onChange={(v)=>setVal(i,"label",v)} />
          <TextArea label="Note" value={sec.note} onChange={(v)=>setVal(i,"note",v)} rows={3} />

          <label className="form-label fw-semibold">Items</label>
          {(sec.items || []).map((it, idx) => (
            <div key={idx} className="d-flex align-items-center gap-2 mb-2">
              <input className="form-control form-control-sm" value={it} onChange={(e)=>setItem(i,idx,e.target.value)} />
              <button className="btn btn-sm btn-outline-danger" onClick={()=>rmItem(i,idx)}>Remove</button>
            </div>
          ))}
          <button className="btn btn-sm btn-outline-primary" onClick={()=>addItem(i)}>+ Add item</button>
        </div>
      ))}
    </div>
  );
}

function TripleListEditor({ title, data, setData, keyMap }) {
  // Generic editor for arrays of objects with 3 fields
  const add = () => setData([...(data || []), { [keyMap[0]]: null, [keyMap[1]]: null, [keyMap[2]]: null }]);
  const rm = (i) => { const arr = [...data]; arr.splice(i,1); setData(arr); };
  const move = (i, dir) => {
    const j = i + dir;
    if (j < 0 || j >= data.length) return;
    const arr = [...data];
    [arr[i], arr[j]] = [arr[j], arr[i]];
    setData(arr);
  };
  const setField = (i, k, v) => {
    const arr = [...data];
    arr[i] = { ...arr[i], [k]: v };
    setData(arr);
  };

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-2">
        <h6 className="m-0">{title}</h6>
        <button className="btn btn-sm btn-outline-primary" onClick={add}>+ Add</button>
      </div>
      {(data || []).map((row, i) => (
        <div key={i} className="border rounded-3 p-2 mb-2 bg-white">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <div className="d-flex gap-2">
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i,-1)}>↑</button>
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i, 1)}>↓</button>
            </div>
            <button className="btn btn-sm btn-outline-danger" onClick={()=>rm(i)}>Remove</button>
          </div>
          <Text label={keyMap[0]} value={row[keyMap[0]]} onChange={(v)=>setField(i,keyMap[0],v)} />
          <Text label={keyMap[1]} value={row[keyMap[1]]} onChange={(v)=>setField(i,keyMap[1],v)} />
          <TextArea label={keyMap[2]} value={row[keyMap[2]]} onChange={(v)=>setField(i,keyMap[2],v)} rows={3} />
        </div>
      ))}
    </div>
  );
}

function ReferencesEditor({ data, setData }) {
  const add = () => setData([...(data || []), { name: "", relationship_or_title: "", contact: "" }]);
  const rm = (i) => { const arr = [...data]; arr.splice(i,1); setData(arr); };
  const move = (i, dir) => {
    const j = i + dir;
    if (j < 0 || j >= data.length) return;
    const arr = [...data];
    [arr[i], arr[j]] = [arr[j], arr[i]];
    setData(arr);
  };
  const setField = (i, k, v) => {
    const arr = [...data];
    arr[i] = { ...arr[i], [k]: v };
    setData(arr);
  };

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-2">
        <h6 className="m-0">References</h6>
        <button className="btn btn-sm btn-outline-primary" onClick={add}>+ Add</button>
      </div>
      {(data || []).map((row, i) => (
        <div key={i} className="border rounded-3 p-2 mb-2 bg-white">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <div className="d-flex gap-2">
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i,-1)}>↑</button>
              <button className="btn btn-sm btn-outline-secondary" onClick={()=>move(i, 1)}>↓</button>
            </div>
            <button className="btn btn-sm btn-outline-danger" onClick={()=>rm(i)}>Remove</button>
          </div>
          <Text label="Name" value={row.name} onChange={(v)=>setField(i,"name",v)} />
          <Text label="Relationship/Title" value={row.relationship_or_title} onChange={(v)=>setField(i,"relationship_or_title",v)} />
          <Text label="Contact" value={row.contact} onChange={(v)=>setField(i,"contact",v)} />
        </div>
      ))}
    </div>
  );
}


/* ============ Main Editor with Section Ordering ============ */
export default function ResumeLocalEditor({ title = "Resume JSON Editor (Local Only)" }) {
  // Load data: prefer localStorage → fallback to empty defaults
  const [order, setOrder] = useState(defaultOrder());
  const [status, setStatus] = useState("");
  const [data, setData] = useState(() => ensureShape(defaultData()));
  const [booting, setBooting] = useState(true);

  // Word count
  const wordCount = useMemo(() => countWords(data), [data]);
  const isOverLimit = wordCount > MAX_WORDS;

  // initial load
  useEffect(() => {
 try {
    const saved = localStorage.getItem(LS_DATA);
    const parsed = saved ? JSON.parse(saved) : ensureShape(defaultData());
    setData(ensureShape(parsed));
  } catch {
    setData(defaultData());
  }
  try {
    const savedOrder = localStorage.getItem(LS_ORDER);
    setOrder(savedOrder ? JSON.parse(savedOrder) : defaultOrder());
  } finally {
    setBooting(false);
  }
}, []);

 // autosave (skip during boot, skip if over word limit)
 useEffect(() => {
   if (booting || !data) return;
   const words = countWords(data);
   if (words > MAX_WORDS) {
     setStatus("Over word limit!");
     return;
   }
   try {
     localStorage.setItem(LS_DATA, JSON.stringify(data));
     setStatus("Saved ✓");
     const t = setTimeout(() => setStatus(""), 800);
     return () => clearTimeout(t);
   } catch {}
 }, [booting, data]);

   useEffect(() => {
     if (booting) return;
     try {
       localStorage.setItem(LS_ORDER, JSON.stringify(order));
     } catch {}
   }, [booting, order]);

   useEffect(() => {
     if (booting) return;
     try {
       const saved = localStorage.getItem(LS_DATA);
       const parsed = saved ? JSON.parse(saved) : ensureShape(defaultData());
    setData(ensureShape(parsed));
  } finally {
    setBooting(false);
  }
}, []);

  if (!data) return <div className="p-3 text-muted">Loading…</div>;

  // Section controls
  const listedSections = useMemo(() => {
    // core keys mapped to renderers
    const core = [
      { key: "profile", label: "Profile" },
      { key: "skills", label: "Skills" },
      { key: "education", label: "Education" },
      { key: "experience", label: "Experience" },
      { key: "references", label: "References" },
    ];
    // custom sections appear as custom:idx
    const customs = (data.custom_sections || []).map((_, i) => ({
      key: `custom:${i}`,
      label: `${data.custom_sections[i]?.label || `Section ${i+1}`}`,
    }));

    const def = [...core, ...customs];
    const dict = Object.fromEntries(def.map((x) => [x.key, x]));
    // Ensure order array includes all present keys; append any missing at the end.
    const merged = [
      ...order.filter((k) => dict[k]),
      ...def.map((x) => x.key).filter((k) => !order.includes(k)),
    ];
    return merged.map((k) => dict[k]);
  }, [order, data?.custom_sections]);

  const moveSection = (idx, dir) => {
    const j = idx + dir;
    if (j < 0 || j >= listedSections.length) return;
    const keys = listedSections.map((s) => s.key);
    [keys[idx], keys[j]] = [keys[j], keys[idx]];
    setOrder(keys);
  };




const renderSection = (secKey) => {
  switch (secKey) {
    case "profile":
      return (
        <>
          <div className="row g-2">
            <div className="col-md-6"><Text label="Name" value={data.name} onChange={(v)=>setData({ ...data, name: v })} /></div>
            <div className="col-md-6"><Text label="Title" value={data.title} onChange={(v)=>setData({ ...data, title: v })} /></div>
          </div>
          <ContactsEditor data={data} setData={setData} />
          <hr />
          <ProfileEditor data={data} setData={setData} />
        </>
      );
    case "skills":
      return <SkillsEditor data={data} setData={setData} />;
    case "education":
      return (
        <TripleListEditor
          title="Education"
          data={data.education}
          setData={(arr)=>setData({ ...data, education: arr })}
          keyMap={["education", "date", "description"]}
        />
      );
    case "experience":
      return (
        <TripleListEditor
          title="Experience"
          data={data.experience}
          setData={(arr)=>setData({ ...data, experience: arr })}
          keyMap={["position_or_company", "date", "description"]}
        />
      );
    case "references":
      return (
        <ReferencesEditor
          data={data.references}
          setData={(arr)=>setData({ ...data, references: arr })}
        />
      );
    default:
      if (secKey.startsWith("custom:")) {
        const idx = Number(secKey.split(":")[1] || 0);

        const handleDelete = () => {
          // 1) remove the section at idx
          const next = clone(data);
          next.custom_sections = (next.custom_sections || []).filter((_, i) => i !== idx);
          setData(next);

          // 2) fix the order keys (custom indices shift)
          setOrder((prev) => {
            // drop the removed key and reindex the rest
            const dropped = prev.filter((k) => k !== `custom:${idx}`);
            return dropped.map((k) => {
              if (!k.startsWith("custom:")) return k;
              const cur = Number(k.split(":")[1] || 0);
              return cur > idx ? `custom:${cur - 1}` : k;
            });
          });
        };

        return (
          <CustomSectionEditorSingle
            index={idx}
            data={data}
            setData={setData}
            onDelete={handleDelete}
          />
        );
      }
      return null;
  }
};


  const addCustomSectionAndFocus = () => {
    const next = clone(data);
    next.custom_sections = Array.isArray(next.custom_sections) ? next.custom_sections : [];
    next.custom_sections.push({ label: "Custom", items: [] });
    setData(next);
    // ensure order contains the new key
    const newKey = `custom:${next.custom_sections.length - 1}`;
    setOrder((prev) => [...prev, newKey]);
  };

  const resetToSeed = () => {
    const seed = ensureShape(defaultData());
    setData(seed);
    setOrder(defaultOrder());
  };

  return (
    <div className="editor-root">
        { !data ? (<div className="p-3 text-muted">Loading…</div>):

     (<>
     <div className="editor-header mb-3">
        <div className="editor-header-top">
          <h5 className="editor-title m-0">{title}</h5>
          <span className={`badge ${isOverLimit ? 'bg-danger' : 'bg-secondary'}`}>
            {wordCount.toLocaleString()} / {MAX_WORDS.toLocaleString()} words
          </span>
        </div>
        <div className="editor-header-actions">
          <button className="btn btn-sm btn-outline-primary" onClick={addCustomSectionAndFocus}>
            + Custom
          </button>
          <button className="btn btn-sm btn-outline-danger" onClick={resetToSeed}>
            Reset
          </button>
          {status && <span className="text-success small ms-2">{status}</span>}
        </div>
      </div>
      {isOverLimit && (
        <div className="alert alert-danger mb-3">
          Your resume exceeds the {MAX_WORDS.toLocaleString()} word limit. Please reduce the content to save.
        </div>
      )}

      {/* Section Order Controller */}
      <div className="card editor-section-card border-0 shadow-sm mb-3">
        <div className="card-header editor-section-header bg-white">
          <strong className="editor-section-label">Section Order</strong>
          <span className="text-muted small">(drag to reorder)</span>
        </div>
        <div className="card-body p-3">
          {listedSections.map((s, i) => (
            <div key={s.key} className="order-item">
              <div className="order-item-info">
                <span className="badge text-bg-secondary">{i + 1}</span>
                <span className="order-item-label">{s.label}</span>
              </div>
              <div className="order-item-actions">
                <button className="btn btn-sm btn-outline-secondary" onClick={()=>moveSection(i,-1)}>↑</button>
                <button className="btn btn-sm btn-outline-secondary" onClick={()=>moveSection(i, 1)}>↓</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Editor for selected/visible sections in order */}
      {listedSections.map((s, i) => (
        <div key={`edit-${s.key}`} className="card editor-section-card border-0 shadow-sm mb-3">
          <div className="card-header editor-section-header bg-white">
            <span className="badge text-bg-secondary">{i + 1}</span>
            <strong className="editor-section-label">{s.label}</strong>
          </div>
          <div className="card-body">{renderSection(s.key)}</div>
        </div>
      ))}
      </> 
        )  }
    </div>
    
  );
}
