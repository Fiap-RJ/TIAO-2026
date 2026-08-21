/**
 * Mapeia `categoria_impacto` (texto vindo do laudo) para um nível neutro e uma
 * paleta Tailwind NÃO alarmista (A2). Regras do spec:
 *  - nunca usar vermelho puro nem termos como "risco alto"/"perigo";
 *  - manter a identidade visual (genera-magenta) para o nível de maior atenção.
 *
 * Níveis neutros: baixo / moderado / atencao.
 */

export const NIVEIS = {
  baixo: {
    nivel: 'baixo',
    label: 'Baixo',
    // verde-acinzentado suave
    badgeClasses: 'bg-emerald-50 text-emerald-800 border border-emerald-200',
  },
  moderado: {
    nivel: 'moderado',
    label: 'Moderado',
    // âmbar neutro
    badgeClasses: 'bg-amber-50 text-amber-800 border border-amber-200',
  },
  atencao: {
    nivel: 'atencao',
    label: 'Atenção',
    // magenta suave, alinhado à identidade Genera (nunca vermelho puro);
    // usa o tom mais escuro (magentahover) para contraste de texto >= 4.5:1
    badgeClasses: 'bg-pink-50 text-genera-magentahover border border-pink-200',
  },
};

/**
 * Correspondência entre os valores de `categoria_impacto` observados no laudo
 * estruturado e os níveis neutros.
 */
export const CATEGORIA_PARA_NIVEL = {
  'Cuidados relevantes': 'baixo',
  'Pontos de atenção': 'moderado',
  'Intervenção médica recomendada': 'atencao',
};

/**
 * Retorna o descritor de nível para uma categoria de impacto.
 * Categorias desconhecidas caem em "moderado" (neutro), nunca em algo alarmista.
 */
export function getRiskLevel(categoriaImpacto) {
  const nivel = CATEGORIA_PARA_NIVEL[categoriaImpacto] ?? 'moderado';
  return NIVEIS[nivel];
}
