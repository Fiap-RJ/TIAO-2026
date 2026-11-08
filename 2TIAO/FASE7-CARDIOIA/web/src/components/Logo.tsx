export function Logo({ tamanho = 28 }: { tamanho?: number }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" aria-hidden="true">
      <path
        d="M16 28s-11-6.6-11-15A6 6 0 0 1 16 9.5 6 6 0 0 1 27 13c0 8.4-11 15-11 15z"
        fill="var(--marca)"
      />
      <path
        d="M7 16h5l2-4 3 8 2-4h6"
        fill="none"
        stroke="#fff"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
