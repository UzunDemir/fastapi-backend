import React from 'react';

const FileUploader = ({ onTextExtracted }) => {
  const handleFiles = async (e) => {
    const files = Array.from(e.target.files);
    const results = [];

    for (let file of files) {
      const reader = new FileReader();
      const promise = new Promise(resolve => {
        reader.onload = () => {
          resolve({ name: file.name, content: reader.result });
        };
      });
      reader.readAsText(file); // для pdf/docx нужен сервер или WASM
      results.push(promise);
    }

    const loaded = await Promise.all(results);
    onTextExtracted(loaded);
  };

  return (
    <div>
      <input type="file" multiple onChange={handleFiles} accept=".txt,.pdf,.docx" />
    </div>
  );
};

export default FileUploader;