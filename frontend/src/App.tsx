import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Aqui definimos que o arquivo pode ser um File ou null
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [imgProcessada, setImgProcessada] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // O '(event: any)' é para o TypeScript não reclamar do tipo do evento
  const selecionarArquivo = (event: any) => {
    if (event.target.files && event.target.files[0]) {
        setArquivo(event.target.files[0]);
    }
  };

  const enviarProva = async () => {
    if (!arquivo) {
      alert("Selecione uma foto primeiro!");
      return;
    }

    const formData = new FormData();
    formData.append("file", arquivo);

    try {
      setLoading(true);
      // Envia para o Backend
      const resposta = await axios.post("http://127.0.0.1:8000/enviar-prova/1", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      console.log("Resposta do Python:", resposta.data);
      
      const nomeImagem = resposta.data.arquivo_processado;
      setImgProcessada(`http://127.0.0.1:8000/imagens/${nomeImagem}`);
      
    } catch (erro) {
      console.error("Deu ruim:", erro);
      alert("Erro ao enviar a prova. Veja o console (F12).");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>📷 Scanner AnalisaEdu</h1>
      
      <div className="card">
        <input type="file" onChange={selecionarArquivo} accept="image/*" />
        
        <button onClick={enviarProva} disabled={loading}>
          {loading ? "Processando..." : "Enviar Prova"}
        </button>
      </div>

      {imgProcessada && (
        <div className="resultado">
          <h3>✨ Visão Computacional:</h3>
          <img src={imgProcessada} alt="Prova Processada" width="400" />
        </div>
      )}
    </div>
  );
}

export default App;