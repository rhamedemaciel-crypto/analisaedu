import React, { useEffect, useState } from 'react';

// Definimos o formato dos dados que vêm do banco
interface Resposta {
  id: number;
  aluno_id: number;
  status: string;
  nota_final: number;
  texto_transcrito: string;
  url_foto_cartao?: string;
  url_foto_redacao?: string;
}

// AQUI ESTAVA O ERRO: Precisa ter 'export' antes do 'const'
export const ListaResultados = () => {
  const [resultados, setResultados] = useState<Resposta[]>([]);

  const carregarDados = async () => {
    try {
      // Tenta buscar da rota de respostas. Se não existir, a lista fica vazia sem travar o site.
      const res = await fetch('http://localhost:8000/respostas'); 
      if (res.ok) {
        const data = await res.json();
        setResultados(data);
      } else {
        console.warn("Rota /respostas não encontrada ou retornou erro.");
      }
    } catch (error) {
      console.error("Erro ao conectar com o backend:", error);
    }
  };

  // Carrega os dados assim que o componente aparece na tela
  useEffect(() => { carregarDados(); }, []);

  return (
    <div style={{ marginTop: '40px', padding: '20px', background: '#fff', borderRadius: '8px', color: '#333', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0 }}>📊 Resultados Recentes</h3>
        <button 
          onClick={carregarDados} 
          style={{ padding: '8px 15px', fontSize: '14px', cursor: 'pointer', background: '#eee', border: 'none', borderRadius: '4px' }}
        >
          🔄 Atualizar
        </button>
      </div>
      
      {resultados.length === 0 ? (
        <p style={{ color: '#666', fontStyle: 'italic' }}>Nenhuma correção encontrada ainda.</p>
      ) : (
        <table border={0} style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: '#f4f4f4', textAlign: 'left' }}>
              <th style={{ padding: '10px' }}>ID Aluno</th>
              <th style={{ padding: '10px' }}>Tipo</th>
              <th style={{ padding: '10px' }}>Status</th>
              <th style={{ padding: '10px' }}>Resultado</th>
            </tr>
          </thead>
          <tbody>
            {resultados.map((res) => (
              <tr key={res.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>#{res.aluno_id}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '12px', 
                    fontSize: '12px',
                    backgroundColor: res.url_foto_cartao ? '#e3f2fd' : '#e8f5e9',
                    color: res.url_foto_cartao ? '#1565c0' : '#2e7d32'
                  }}>
                    {res.url_foto_cartao ? 'Gabarito' : 'Redação'}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>{res.status}</td>
                <td style={{ padding: '10px', maxWidth: '300px' }}>
                  {res.texto_transcrito 
                    ? <span title={res.texto_transcrito}>{res.texto_transcrito.substring(0, 50)}...</span> 
                    : <strong>Nota: {res.nota_final}</strong>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};