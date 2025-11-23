import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// *** Ícones SVG Inline (Substituindo lucide-react para evitar conflitos) ***
const IconRefresh = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
    <path d="M3 21v-5h5" />
  </svg>
);

const IconLayoutGrid = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="7" height="7" x="3" y="3" rx="1" />
    <rect width="7" height="7" x="14" y="3" rx="1" />
    <rect width="7" height="7" x="14" y="14" rx="1" />
    <rect width="7" height="7" x="3" y="14" rx="1" />
  </svg>
);

const IconImage = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
    <circle cx="9" cy="9" r="2" />
    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
  </svg>
);

// *** IMPORTANTE: Substitua pela URL da sua Azure Function App ***
const API_BASE_URL = "https://fa-galeriadeartes.azurewebsites.net/api/galeria";

const App = () => {
  const [obras, setObras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Função para buscar as obras da API
  const fetchObras = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_BASE_URL);
      if (!response.ok) {
        throw new Error(`Erro HTTP: Status ${response.status}`);
      }
      const data = await response.json();
      setObras(data);
    } catch (err) {
      console.error("Falha ao buscar obras:", err);
      setError("Falha ao carregar a galeria. Verifique a Azure Function e o CORS.");
      setObras([]);
    } finally {
      setLoading(false);
    }
  };

  // Executa a busca ao carregar a página
  useEffect(() => {
    fetchObras();
  }, []);

  // Renderização da tela de carregamento
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
        <IconRefresh className="w-8 h-8 text-indigo-600 animate-spin" />
        <p className="mt-4 text-gray-700 font-semibold">Carregando Galeria de Artes...</p>
      </div>
    );
  }

  // Renderização da tela de erro
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-red-100 p-4 rounded-xl shadow-lg m-4">
        <p className="text-xl font-bold text-red-700">Erro na API</p>
        <p className="mt-2 text-red-600 text-center">{error}</p>
        <button
          onClick={fetchObras}
          className="mt-6 px-4 py-2 bg-red-600 text-white rounded-lg shadow-md hover:bg-red-700 transition duration-150 flex items-center"
        >
          <IconRefresh className="w-5 h-5 mr-2" /> Tentar Novamente
        </button>
      </div>
    );
  }

  // Renderização da galeria principal
  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-10 font-sans">
      <header className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-extrabold text-indigo-800 tracking-tight flex items-center justify-center">
          <IconLayoutGrid className="inline-block w-8 h-8 mr-3 mb-1 text-indigo-500" />
          Galeria de Artes Online
        </h1>
        <p className="text-gray-600 mt-2 text-lg">Obras de arte consumidas via Azure Function (MySQL & Blob Storage)</p>
      </header>

      {obras.length === 0 ? (
        <div className="text-center p-10 bg-white rounded-xl shadow-md">
          <IconImage className="w-12 h-12 text-gray-400 mx-auto" />
          <p className="mt-4 text-xl font-semibold text-gray-700">Nenhuma obra encontrada.</p>
          <p className="text-gray-500">Verifique se há dados na tabela MySQL e se a API está funcionando.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {obras.map((obra, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
            >
              <div className="relative h-64 w-full">
                <img
                  src={obra.url_imagem}
                  alt={obra.nome}
                  className="w-full h-full object-cover transition-opacity duration-500"
                  onError={(e) => {
                    // Fallback caso a imagem não carregue
                    e.target.onerror = null;
                    e.target.src = "https://placehold.co/600x400/CCCCCC/333333?text=Imagem+Indisponivel";
                  }}
                  loading="lazy"
                />
              </div>
              <div className="p-5">
                <h2 className="text-2xl font-bold text-gray-900 mb-1">{obra.nome}</h2>
                <p className="text-indigo-600 font-medium mb-3 border-b pb-2 border-indigo-100">{obra.artista}</p>
                <p className="text-gray-700 text-sm line-clamp-3">{obra.descricao}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <footer className="mt-16 text-center text-gray-500 text-sm">
        <p>&copy; {new Date().getFullYear()} Galeria de Artes Azure. Backend: fa-galeriadeartes.</p>
      </footer>
    </div>
  );
};

// Montagem do React no DOM
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
} else {
  // Fallback caso o elemento root não exista, cria um
  const newRoot = document.createElement('div');
  newRoot.id = 'root';
  document.body.appendChild(newRoot);
  const root = createRoot(newRoot);
  root.render(<App />);
}

export default App;