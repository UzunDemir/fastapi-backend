import React from 'react';

const TextPreview = ({ documents }) => {
  return (
    <div>
      {documents.map((doc, i) => (
        <div key={i}>
          <h4>{doc.name}</h4>
          <pre style={{ maxHeight: 200, overflowY: 'scroll', background: '#f9f9f9' }}>
            {doc.content.slice(0, 2000)}
          </pre>
        </div>
      ))}
    </div>
  );
};

export default TextPreview;