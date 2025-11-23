import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// Pega a <div id="root"> do public/index.html
const rootElement = document.getElementById('root');

// Cria o root do React 18
const root = createRoot(rootElement);

// Renderiza a aplicação
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
