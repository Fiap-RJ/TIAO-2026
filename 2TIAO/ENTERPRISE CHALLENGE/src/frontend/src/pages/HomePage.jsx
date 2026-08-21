import { Link } from 'react-router-dom';

const SECOES = [
  {
    to: '/riscos',
    titulo: 'Riscos e predisposições',
    descricao:
      'Cards por painel genético (Skin, Fit, Nutri, Farma) com linguagem clara e não alarmista.',
  },
  {
    to: '/ancestralidade',
    titulo: 'Resumo de ancestralidade',
    descricao: 'Composição de ancestralidade a partir do seu perfil genético.',
  },
  {
    to: '/chat',
    titulo: 'Converse com seu laudo',
    descricao:
      'Tire dúvidas sobre suas predisposições com o assistente especializado.',
  },
  {
    to: '/historico',
    titulo: 'Histórico de interações',
    descricao: 'Reveja as perguntas e respostas anteriores.',
  },
];

/** HomePage — landing do dashboard (A1). */
export default function HomePage() {
  return (
    <section>
      <h1 className="text-2xl font-bold text-genera-roxo">
        Bem-vindo ao seu dashboard genético
      </h1>
      <p className="mt-2 max-w-2xl text-genera-roxo/70">
        Explore seus resultados de forma simples e responsável. Escolha uma das
        seções abaixo para começar.
      </p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {SECOES.map((secao) => (
          <Link
            key={secao.to}
            to={secao.to}
            className="rounded-xl border border-gray-200 p-5 shadow-sm transition-shadow hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
          >
            <h2 className="text-lg font-semibold text-genera-roxo">
              {secao.titulo}
            </h2>
            <p className="mt-1 text-sm text-genera-roxo/70">{secao.descricao}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
