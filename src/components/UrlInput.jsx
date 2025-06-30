import React, { useState } from 'react';
import axios from 'axios';

const UrlInput = ({ onTextExtracted }) => {
  const [urls, setUrls] = useState("");

  const handleLoad = async () => {
    const urlList = urls.split('\n').map(u => u.trim()).filter(Boolean);
    const results = [];

    for (let url of urlList) {
      try {
        const response = await axios.get(url, { responseType: 'blob' });
        const text = await response.data.text();
        results.push({ name: url, content: text });
      } catch (error) {
        results.push({ name: url, content: 'Ошибка загрузки: ' + error.message });
      }
    }

    onTextExtracted(results);
  };

  return (
    <div>
      <textarea
        rows={5}
        value={urls}
        onChange={e => setUrls(e.target.value)}
        placeholder="Вставьте URL-адреса по одному в строке"
      />
      <button onClick={handleLoad}>Загрузить из URL</button>
    </div>
  );
};

export default UrlInput;