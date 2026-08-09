"use client";

import { useMemo, useState } from "react";
import vendorsData from "../data/vendors.json";
import librariesData from "../data/libraries.json";
import instrumentsData from "../data/instruments.json";
import articulationsData from "../data/articulations.json";
import contextsData from "../data/contexts.json";

type Entity = { id: string; name: string; aliases: string[] };
type Library = Entity & {
  vendorId: string;
  sourceUrl?: string;
  instrumentIds?: string[];
  articulationIds?: string[];
};

const vendors = vendorsData.vendors as Entity[];
const libraries = librariesData.libraries as Library[];
const instruments = instrumentsData.instruments as Entity[];
const articulations = articulationsData.articulations as Entity[];
const contexts = contextsData.contexts as Array<{
  libraryId: string;
  instrumentAliases?: Record<string, string | string[]>;
  articulationAliases?: Record<string, string | string[]>;
  instrumentArticulations?: Record<string, string[]>;
}>;

function findEntity(items: Entity[], id: string) {
  return items.find((item) => item.id === id);
}

function SelectBox({
  label,
  value,
  onChange,
  items,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  items: Entity[];
  placeholder: string;
}) {
  const sortedItems = [...items].sort((left, right) => left.name.localeCompare(right.name));

  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{placeholder}</option>
        {sortedItems.map((item) => (
          <option value={item.id} key={item.id}>
            {item.name}
          </option>
        ))}
      </select>
    </label>
  );
}

function Detail({ title, entity }: { title: string; entity?: Entity & { sourceUrl?: string } }) {
  if (!entity) {
    return <div className="empty-detail">Select a {title.toLowerCase()} to inspect it.</div>;
  }

  return (
    <div className="detail-card">
      <div className="detail-heading">
        <span className="eyebrow">{title}</span>
        <code>{entity.id}</code>
      </div>
      <h2>{entity.name}</h2>
      {entity.sourceUrl && <a className="source-link" href={entity.sourceUrl} target="_blank" rel="noreferrer">Open source page ↗</a>}
      <div className="alias-label">Recognized abbreviations & aliases</div>
      <div className="aliases">
        {entity.aliases.length ? entity.aliases.map((alias) => <span key={alias}>{alias}</span>) : <span>None listed</span>}
      </div>
    </div>
  );
}

export default function Home() {
  const [vendorId, setVendorId] = useState("");
  const [libraryId, setLibraryId] = useState("");
  const [instrumentId, setInstrumentId] = useState("");
  const [articulationId, setArticulationId] = useState("");
  const [copyStatus, setCopyStatus] = useState("");

  const selectedLibrary = findEntity(libraries, libraryId) as Library | undefined;
  const selectedContext = contexts.find((context) => context.libraryId === libraryId);

  const visibleLibraries = useMemo(
    () => libraries.filter((library) => !vendorId || library.vendorId === vendorId),
    [vendorId],
  );
  const visibleInstruments = useMemo(() => {
    if (!selectedLibrary?.instrumentIds) return instruments;
    return instruments.filter((instrument) => selectedLibrary.instrumentIds?.includes(instrument.id));
  }, [selectedLibrary]);
  const visibleArticulations = useMemo(() => {
    const instrumentArticulations = selectedContext?.instrumentArticulations?.[instrumentId];
    if (instrumentArticulations) {
      return articulations.filter((articulation) => instrumentArticulations.includes(articulation.id));
    }
    if (!selectedLibrary?.articulationIds) return articulations;
    return articulations.filter((articulation) => selectedLibrary.articulationIds?.includes(articulation.id));
  }, [instrumentId, selectedContext, selectedLibrary]);

  const selectedVendor = findEntity(vendors, vendorId);
  const selectedInstrument = findEntity(instruments, instrumentId);
  const selectedArticulation = findEntity(articulations, articulationId);
  const contextualInstrumentAliases = selectedContext?.instrumentAliases ?? {};
  const contextualArticulationAliases = selectedContext?.articulationAliases ?? {};
  const allSelected = Boolean(selectedVendor && selectedLibrary && selectedInstrument && selectedArticulation);
  const clipboardValue = [selectedVendor, selectedLibrary, selectedInstrument, selectedArticulation]
    .map((entity) => entity?.aliases[0] ?? entity?.id ?? "")
    .join("_");

  async function copyAbbreviations() {
    if (!allSelected) return;
    await navigator.clipboard.writeText(clipboardValue);
    setCopyStatus("Copied");
    window.setTimeout(() => setCopyStatus(""), 1600);
  }

  function changeVendor(value: string) {
    setVendorId(value);
    if (libraryId && !libraries.find((library) => library.id === libraryId && library.vendorId === value)) {
      setLibraryId("");
      setInstrumentId("");
      setArticulationId("");
    }
  }

  function changeLibrary(value: string) {
    setLibraryId(value);
    setInstrumentId("");
    setArticulationId("");
    const library = libraries.find((item) => item.id === value);
    if (library && vendorId !== library.vendorId) setVendorId(library.vendorId);
  }

  function changeInstrument(value: string) {
    setInstrumentId(value);
    setArticulationId("");
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark">OT</div>
        <div>
          <div className="brand-name">Orch Terminology</div>
          <div className="brand-subtitle">OwnLife Audio · shared database browser</div>
        </div>
        <div className="data-status"><span /> canonical data</div>
      </header>

      <section className="hero">
        <div>
          <div className="kicker">Terminology atlas</div>
          <h1>Find the language<br /><em>behind the patch.</em></h1>
          <p>Browse canonical names, abbreviations, and library-specific meanings across the orchestral toolkit.</p>
        </div>
        <div className="hero-note"><span>01</span><br />Choose a path<br />through the catalog</div>
      </section>

      <section className="browser-panel" aria-label="Terminology browser">
        <div className="panel-heading">
          <div><span className="eyebrow">Contextual lookup</span><h2>Build a terminology path</h2></div>
          <button className="reset" onClick={() => { setVendorId(""); setLibraryId(""); setInstrumentId(""); setArticulationId(""); }}>Reset</button>
        </div>
        <div className="selectors">
          <SelectBox label="Vendor" value={vendorId} onChange={changeVendor} items={vendors} placeholder="All vendors" />
          <SelectBox label="Library" value={libraryId} onChange={changeLibrary} items={visibleLibraries} placeholder="All libraries" />
          <SelectBox label="Instrument" value={instrumentId} onChange={changeInstrument} items={visibleInstruments} placeholder="All instruments" />
          <SelectBox label="Articulation" value={articulationId} onChange={setArticulationId} items={visibleArticulations} placeholder="All articulations" />
        </div>
        {(Object.keys(contextualInstrumentAliases).length > 0 || Object.keys(contextualArticulationAliases).length > 0) && (
          <div className="context-note"><strong>Context active:</strong> this library defines local meanings for selected aliases.</div>
        )}
      </section>

      <section className="results">
        <div className="result-intro"><span className="eyebrow">Selected records</span><h2>Details</h2><p>Every record exposes its canonical identifier and known shorthand.</p>
          {allSelected && <>
            <div className="clipboard-preview"><span>Clipboard string</span><code>{clipboardValue}</code></div>
            <button className="copy-button" onClick={copyAbbreviations}>{copyStatus || "Copy abbreviations to clipboard"}</button>
          </>}
        </div>
        <div className="detail-grid">
          <Detail title="Vendor" entity={selectedVendor} />
          <Detail title="Library" entity={selectedLibrary} />
          <Detail title="Instrument" entity={selectedInstrument} />
          <Detail title="Articulation" entity={selectedArticulation} />
        </div>
      </section>

      <footer><span>ORCH TERMINOLOGY</span><span>{vendors.length} vendors · {libraries.length} libraries · {instruments.length} instruments · {articulations.length} articulations</span></footer>
    </main>
  );
}
