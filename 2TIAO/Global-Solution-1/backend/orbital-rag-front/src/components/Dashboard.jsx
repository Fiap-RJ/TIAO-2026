import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Radio, ShieldCheck } from 'lucide-react';

export function Dashboard() {
  // Estado que vai guardar os dados vindos da NASA
  const [eventos, setEventos] = useState([]);

  // O useEffect simula a busca dos dados assim que a tela carrega
  useEffect(() => {
        const dadosNasaMock = [
      {
        id_evento: "AST-2026-001",
        tipo: "Asteroide",
        nome: "Apophis",
        data_aproximacao: "2026-06-15",
        distancia_terra_km: 5000000,
        risco_colisao: false,
        resumo_alerta: "Asteroide de grande porte a passar a uma distância segura. Risco descartado."
      },
      {
        id_evento: "CME-2026-089",
        tipo: "Tempestade Solar",
        nome: "Ejeção de Massa Coronal Classe X",
        data_aproximacao: "2026-06-08",
        distancia_terra_km: 150000000,
        risco_colisao: true,
        resumo_alerta: "Tempestade geomagnética severa detetada. Risco de interferência em satélites."
      }
    ];
    
    // Guardamos os dados no estado do React
    setEventos(dadosNasaMock);
  }, []);

  // --- MATEMÁTICA DINÂMICA ---
  // Conta quantos eventos existem no total
  const totalMonitorizados = eventos.length;
  // Filtra e conta apenas os eventos que têm risco_colisao === true
  const alertasCriticos = eventos.filter(evento => evento.risco_colisao === true).length;

  return (
    <div style={{ padding: '20px', color: '#333', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Painel de Controlo Orbital</h2>
      <p>Monitorização em tempo real do ecossistema espacial</p>

      {/* --- SECÇÃO 1: RESUMO DINÂMICO --- */}
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px', flexWrap: 'wrap' }}>
        
        {/* Cartão de Comunicação (Fixo) */}
        <div style={{ border: '1px solid #333', padding: '20px', borderRadius: '0px', backgroundColor: '#0b3d91', color: 'white', flex: '1', minWidth: '200px'}}>
          <Radio color="blue" size={30} />
          <h3>Comunicação</h3>
          <p style={{ color: 'green', fontWeight: 'bold' }}>Sistemas Online</p>
        </div>

        {/* Cartão Dinâmico: Total de Objetos */}
        <div style={{ border: '1px solid #333', padding: '20px', borderRadius: '0px', backgroundColor: '#0b3d91', color: 'white', flex: '1', minWidth: '200px'}}>
          <Activity color="purple" size={30} />
          <h3>Objetos Monitorizados</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>{totalMonitorizados}</p>
          <small>Eventos ativos na base de dados</small>
        </div>

        {/* Cartão Dinâmico: Alertas (Muda de cor consoante o risco) */}
        <div style={{ border: `2px solid ${alertasCriticos > 0 ? 'red' : '#ccc'}`, padding: '15px', borderRadius: '8px', flex: '1', minWidth: '200px', backgroundColor: alertasCriticos > 0 ? '#0b3d91' : '#fff' }}>
          <AlertTriangle color={alertasCriticos > 0 ? "red" : "orange"} size={30} />
          <h3 style={{ color: alertasCriticos > 0 ? 'red' : 'inherit' }}>Alertas Críticos</h3>
          <p style={{ color: alertasCriticos > 0 ? 'red' : 'orange', fontWeight: 'bold', fontSize: '20px' }}>
            {alertasCriticos} {alertasCriticos === 1 ? 'Risco Detetado' : 'Riscos Detetados'}
          </p>
        </div>
      </div>

      {/* --- SECÇÃO 2: LISTA DETALHADA DE EVENTOS (RENDERIZADA COM .MAP) --- */}
      <h3 style={{ marginTop: '40px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Registo de Eventos da NASA</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
        {eventos.map((evento) => (
          <div key={evento.id_evento} style={{ 
            border: '1px solid #ddd', 
            borderLeft: `5px solid ${evento.risco_colisao ? 'red' : 'green'}`, 
            padding: '15px', 
            borderRadius: '8px',
            backgroundColor: '#fff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h4 style={{ margin: '0 0 5px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                {evento.nome} 
                <span style={{ fontSize: '12px', backgroundColor: '#eee', padding: '3px 8px', borderRadius: '12px', fontWeight: 'normal' }}>
                  {evento.tipo}
                </span>
              </h4>
              <p style={{ margin: '5px 0', fontSize: '14px', color: '#555' }}><strong>Aproximação:</strong> {evento.data_aproximacao} | <strong>Distância:</strong> {evento.distancia_terra_km.toLocaleString('pt-PT')} km</p>
              <p style={{ margin: '5px 0', fontSize: '14px', fontStyle: 'italic' }}>{evento.resumo_alerta}</p>
            </div>
            
            {/* Ícone de status visual à direita */}
            <div>
              {evento.risco_colisao ? (
                <div style={{ color: 'red', textAlign: 'center' }}>
                  <AlertTriangle size={24} />
                  <div style={{ fontSize: '12px', fontWeight: 'bold' }}>PERIGO</div>
                </div>
              ) : (
                <div style={{ color: 'green', textAlign: 'center' }}>
                  <ShieldCheck size={24} />
                  <div style={{ fontSize: '12px', fontWeight: 'bold' }}>SEGURO</div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
