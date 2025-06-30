import React, { useState } from 'react';
import UrlInput from './components/UrlInput';
import FileUploader from './components/FileUploader';
import TextPreview from './components/TextPreview';

function App() {
  const [mode, setMode] = useState("url");
  const [documents, setDocuments] = useState([]);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>📚 Загрузчик в базу знаний</h1>

      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="url">URL список</option>
        <option value="files">Загрузка файлов</option>
      </select>

      {mode === "url" && <UrlInput onTextExtracted={setDocuments} />}
      {mode === "files" && <FileUploader onTextExtracted={setDocuments} />}

      <hr />
      <TextPreview documents={documents} />
    </div>
  );
}

export default App;