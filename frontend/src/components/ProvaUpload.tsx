import React, { useState } from 'react';

// Definimos o que o componente pode receber
interface ProvaUploadProps {
  modo: 'gabarito' | 'redacao';
}

export const ProvaUpload = ({ modo }: ProvaUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [alunoId, setAlunoId] = useState('');

  const handleUpload = async () => {
    if (!file || !alunoId) return alert('Selecione um arquivo e o ID do aluno');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('modo', modo); // Enviamos o modo (gabarito ou redação) para o backend

    try {
      const endpoint = modo === 'gabarito' ? 'enviar-gabarito' : 'analisar-redacao';
      const response = await fetch(`http://localhost:8000/${endpoint}/${alunoId}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      console.log('Resultado:', data);
      alert(`${modo === 'gabarito' ? 'Gabarito' : 'Redação'} processado com sucesso!`);
    } catch (error) {
      console.error('Erro no upload:', error);
    }
  };

  return (
    <div className="upload-box" style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px', background: '#f9f9f9' }}>
      <h3>{modo === 'gabarito' ? '📝 Processar Questões Objetivas' : '✍️ Analisar Redação com IA'}</h3>
      
      <div style={{ marginBottom: '15px' }}>
        <input 
          type="text" 
          placeholder="Matrícula do Aluno" 
          value={alunoId} 
          onChange={(e) => setAlunoId(e.target.value)} 
          style={{ padding: '8px', marginRight: '10px' }}
        />
      </div>

      <div style={{ marginBottom: '15px' }}>
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files?.[0] || null)} 
        />
      </div>

      <button 
        onClick={handleUpload}
        style={{ 
          padding: '10px 20px', 
          backgroundColor: modo === 'gabarito' ? '#007bff' : '#28a745', 
          color: 'white', 
          border: 'none', 
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        Iniciar Processamento ({modo})
      </button>
    </div>
  );
};