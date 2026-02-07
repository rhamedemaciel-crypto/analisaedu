import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [imgResultado, setImgResultado] = useState<string | null>(null);
  const [textoResultado, setTextoResultado] = useState<string | null>(null);
  const [infoExtra, setInfoExtra] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [modo, setModo] = useState<'gabarito' | 'redacao'>('gabarito');

  const selecionarArquivo = (event: any) => {
    if (event.target.files && event.target.files[0]) {
        setArquivo(event.target.files[0]);
        setImgResultado(null);
        setTextoResultado(null);
        setInfoExtra(null);
    }
  };

  const enviarArquivo = async () => {
    if (!arquivo) {
      alert("Selecione uma foto primeiro!");
      return;
    }

    const formData = new FormData();
    formData.append("file", arquivo);

    // Seleciona a rota correta
    const endpoint = modo === 'gabarito' ? 'enviar-gabarito' : 'enviar-redacao';
    const url = `http://127.0.0.1:8000/${endpoint}/1`; 

    try {
      setLoading(true);
      setImgResultado(null);
      setTextoResultado(null);

      const resposta = await axios.post(url, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      console.log("Retorno:", resposta.data);

      if (modo === 'gabarito') {
        // Mostra a imagem com os quadradinhos verdes
        const nomeImagem = resposta.data.arquivo_processado;
        setImgResultado(`http://127.0.0.1:8000/imagens/${nomeImagem}`);
        setInfoExtra(resposta.data.info);
      } else {
        // Mostra o texto da redação
        setTextoResultado(resposta.data.texto_transcrito);
        setImgResultado(`http://127.0.0.1:8000/imagens/${resposta.data.arquivo_original}`);
      }
      
    } catch (erro) {
      console.error("Erro:", erro);
      alert("Erro ao enviar. Verifique o console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>📷 AnalisaEdu Híbrido</h1>
      
      <div className="card">
        {/* BOTÕES DE SELEÇÃO */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '20px' }}>
          <button 
            onClick={() => setModo('gabarito')}
            style={{ 
              backgroundColor: modo === 'gabarito' ? '#646cff' : '#444',
              border: modo === 'gabarito' ? '2px solid white' : 'none'
            }}
          >
            🔢 Corrigir Gabarito
          </button>
          <button 
            onClick={() => setModo('redacao')}
            style={{ 
              backgroundColor: modo === 'redacao' ? '#ff649c' : '#444',
              border: modo === 'redacao' ? '2px solid white' : 'none'
            }}
          >
            📝 Transcrever Redação
          </button>
        </div>

        <p>Modo Atual: <strong>{modo === 'gabarito' ? "GABARITO (Visão Clássica)" : "REDAÇÃO (Inteligência Artificial)"}</strong></p>

        <input type="file" onChange={selecionarArquivo} accept="image/*" />
        
        <br /><br />

        <button onClick={enviarArquivo} disabled={loading} style={{width: '100%'}}>
          {loading ? "Processando..." : "ENVIAR ARQUIVO"}
        </button>
      </div>

      <div className="resultado">
        {infoExtra && <p className="status-badge">{infoExtra}</p>}

        {imgResultado && (
          <div>
            <h3>{modo === 'gabarito' ? 'Resultado da Correção:' : 'Imagem Enviada:'}</h3>
            <img src={imgResultado} alt="Resultado" style={{ maxWidth: '100%', borderRadius: '8px' }} />
          </div>
        )}

        {textoResultado && (
          <div className="box-texto">
            <h3>📝 Transcrição da IA:</h3>
            <div style={{ 
              textAlign: 'left', 
              background: '#2a2a2a', 
              padding: '20px', 
              borderRadius: '8px',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}>
              {textoResultado}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;