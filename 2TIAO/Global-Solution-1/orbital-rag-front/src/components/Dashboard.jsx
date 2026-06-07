import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Radio, ShieldCheck, Loader2 } from 'lucide-react';
import axios from 'axios';

export function Dashboard() {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:3000/api/events')
      .then((res) => setEventos(res.data))
      .catch(() => setErro('Falha ao conectar com o backend. Verifique se está rodando na porta 3000.'))
      .finally(() => setLoading(false));
  }, []);

  const totalMonitorizados = eventos.length;
  const alertasCriticos = eventos.filter(evento => evento.risco_colisao === true).length;

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <Loader2 size={32} className="animate-spin" />
        <p>Carregando dados orbitais...</p>
      </div>
    );
  }

  if (erro) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'red' }}>
        <AlertTriangle size={32} />
        <p>{erro}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', color: '#333', maxWidth: '1000px', margin: '0 auto' }}>
      <h2>Painel de Controlo Orbital</h2>
      <p>Monitorização em tempo real do ecossistema espacial</p>

      {/* RESUMO */}
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px', flexWrap: 'wrap' }}>
        
        <div style={{ border: '1px solid #333', padding: '20px', borderRadius: '0px', backgroundColor: '#0b3d91', color: 'white', flex: '1', minWidth: '200px'}}>
          <Radio color="blue" size={30} />
          <h3>Comunicação</h3>
          <p style={{ color: 'green', fontWeight: 'bold' }}>Sistemas Online</p>
        </div>

        <div style={{ border: '1px solid #333', padding: '20px', borderRadius: '0px', backgroundColor: '#0b3d91', color: 'white', flex: '1', minWidth: '200px'}}>
          <Activity color="purple" size={30} />
          <h3>Objetos Monitorizados</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>{totalMonitorizados}</p>
          <small>Eventos ativos na base de dados</small>
        </div>

        <div style={{ border: `2px solid ${alertasCriticos > 0 ? 'red' : '#ccc'}`, padding: '15px', borderRadius: '8px', flex: '1', minWidth: '200px', backgroundColor: alertasCriticos > 0 ? '#0b3d91' : '#fff' }}>
          <AlertTriangle color={alertasCriticos > 0 ? "red" : "orange"} size={30} />
          <h3 style={{ color: alertasCriticos > 0 ? 'red' : 'inherit' }}>Alertas Críticos</h3>
          <p style={{ color: alertasCriticos > 0 ? 'red' : 'orange', fontWeight: 'bold', fontSize: '20px' }}>
            {alertasCriticos} {alertasCriticos === 1 ? 'Risco Detetado' : 'Riscos Detetados'}
          </p>
        </div>
      </div>

      {/* LISTA DE EVENTOS */}
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
