import React, { useState } from 'react';

interface ProvaUploadProps {
  modo: 'gabarito' | 'redacao';
}

export const ProvaUpload = ({ modo }: ProvaUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [alunoId, setAlunoId] = useState('');
  // Definimos '1' como padrão pois seu seed.py cria a Avaliação ID 1
  const [avaliacaoId, setAvaliacaoId] = useState('1'); 

  const handleUpload = async () => {
    if (!file || !alunoId || !avaliacaoId) return alert('Preencha todos os campos!');
    
    const formData = new FormData();
    formData.append('file', file);
    // O Backend exige este campo específico:
    formData.append('avaliacao_id', avaliacaoId); 

    try {
      // Ajustei para bater na rota certa (/enviar-redacao ou /enviar-gabarito)
      const endpoint = modo === 'gabarito' ? 'enviar-gabarito' : 'enviar-redacao';
      
      const response = await fetch(`http://localhost:8000/${endpoint}/${alunoId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const erro = await response.json();
        throw new Error(erro.detail || 'Erro desconhecido no servidor');
      }

      const data = await response.json();
      console.log('Sucesso:', data);
      alert(`Sucesso! ${modo === 'gabarito' ? 'Gabarito lido' : 'Redação transcrita'}.`);
      
    } catch (error) {
      console.error('Erro no upload:', error);
      alert('Falha no envio. Verifique o console (F12).');
    }
  };

  return (
    <div className="upload-box" style={{ 
      padding: '20px', 
      border: '1px solid #444', 
      borderRadius: '12px', 
      background: '#2a2a2a', 
      color: 'white',
      maxWidth: '500px',
      margin: '0 auto'
    }}>
      <h3>{modo === 'gabarito' ? '📝 Ler Gabarito (OMR)' : '✍️ Transcrever Redação (IA)'}</h3>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
        <input 
          type="number" 
          placeholder="ID Aluno" 
          value={alunoId} 
          onChange={(e) => setAlunoId(e.target.value)} 
          style={{ flex: 1, padding: '10px', borderRadius: '5px', border: 'none' }}
        />
        <input 
          type="number" 
          placeholder="ID Prova" 
          value={avaliacaoId} 
          onChange={(e) => setAvaliacaoId(e.target.value)} 
          style={{ flex: 1, padding: '10px', borderRadius: '5px', border: 'none' }}
        />
      </div>

      <div style={{ marginBottom: '20px', textAlign: 'left' }}>
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files?.[0] || null)} 
          style={{ width: '100%' }}
        />
      </div>

      <button 
        onClick={handleUpload}
        style={{ 
          width: '100%',
          padding: '12px', 
          backgroundColor: modo === 'gabarito' ? '#007bff' : '#28a745', 
          color: 'white', 
          border: 'none', 
          borderRadius: '5px',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '16px'
        }}
      >
        {modo === 'gabarito' ? 'Processar Gabarito' : 'Enviar para IA'}
      </button>
    </div>
  );
};