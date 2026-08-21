import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

/**
 * Paleta de tons distintos alinhada à identidade Genera (roxo/magenta) e a
 * hues complementares — evita vermelho puro e mantém contraste entre fatias.
 */
const CORES = ['#2D004B', '#E6007E', '#7B2FA3', '#00A3A3', '#F5A623', '#5B8DEF'];

/**
 * AncestryChart — composição de ancestralidade (A3).
 *
 * Acessibilidade: além do gráfico (recharts), rendemos uma legenda textual com
 * região + percentual, de modo que a informação não dependa apenas da cor.
 * O container recebe role="img" e um aria-label descritivo.
 */
export default function AncestryChart({ componentes }) {
  const total = componentes.reduce((soma, c) => soma + c.percentual, 0);
  const resumoTexto = componentes
    .map((c) => `${c.regiao} ${c.percentual}%`)
    .join(', ');

  return (
    <div className="grid items-center gap-6 sm:grid-cols-2">
      <div
        role="img"
        aria-label={`Composição de ancestralidade: ${resumoTexto}.`}
        className="h-64 w-full"
      >
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={componentes}
              dataKey="percentual"
              nameKey="regiao"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={2}
              isAnimationActive={false}
            >
              {componentes.map((c, i) => (
                <Cell key={c.regiao} fill={CORES[i % CORES.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(valor, nome) => [`${valor}%`, nome]}
              contentStyle={{ fontSize: '0.875rem' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legenda textual acessível — não depende só de cor */}
      <ul className="space-y-2">
        {componentes.map((c, i) => (
          <li key={c.regiao} className="flex items-center gap-3 text-sm">
            <span
              aria-hidden="true"
              className="inline-block h-3 w-3 shrink-0 rounded-sm"
              style={{ backgroundColor: CORES[i % CORES.length] }}
            />
            <span className="flex-1 text-genera-roxo/80">{c.regiao}</span>
            <span className="font-semibold text-genera-roxo">
              {c.percentual}%
            </span>
          </li>
        ))}
        {Math.round(total) !== 100 && (
          <li className="pt-1 text-xs text-genera-roxo/50">
            Percentuais somam {total.toFixed(1)}% (dados ilustrativos).
          </li>
        )}
      </ul>
    </div>
  );
}
