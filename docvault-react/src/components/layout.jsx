import C from '../styles/tokens'

/* ── Card ── */
export function Card({ children, style }) {
  return (
    <div style={{ background: C.paper, border: `1px solid ${C.line}`, borderRadius: C.r, boxShadow: C.shadow, ...style }}>
      {children}
    </div>
  )
}
export function CardHeader({ title, action }) {
  return (
    <div style={{ padding: '13px 20px', borderBottom: `1px solid ${C.line}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
      <h2 style={{ fontFamily: C.font, fontWeight: 600, fontSize: '.95rem' }}>{title}</h2>
      {action}
    </div>
  )
}

/* ── Modal ── */
export function Modal({ open, onClose, title, children }) {
  if (!open) return null
  return (
    <div
      onClick={e => e.target === e.currentTarget && onClose()}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(13,13,18,.45)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000, padding: '1rem', animation: 'fadeIn .15s ease',
      }}>
      <div style={{
        background: '#fff', borderRadius: C.rLg, padding: '1.75rem',
        width: '100%', maxWidth: 460, boxShadow: C.shadowLg,
        animation: 'slideUp .18s ease',
      }}>
        {title && <h3 style={{ fontFamily: C.font, fontSize: '1.05rem', marginBottom: 12 }}>{title}</h3>}
        {children}
      </div>
    </div>
  )
}

/* ── Page layout ── */
export function Page({ children }) {
  return (
    <div style={{ padding: '2rem 0', animation: 'fadeUp .2s ease' }}>
      <div style={{ maxWidth: 1080, margin: '0 auto', padding: '0 24px' }}>
        {children}
      </div>
    </div>
  )
}
export function PageHead({ title, sub, action }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: '1.75rem' }}>
      <div>
        <h1 style={{ fontFamily: C.font, fontWeight: 700, fontSize: '1.6rem', letterSpacing: '-.03em' }}>{title}</h1>
        {sub && <p style={{ color: C.ink2, fontSize: '.875rem', marginTop: 3 }}>{sub}</p>}
      </div>
      {action}
    </div>
  )
}

/* ── Stat card ── */
export function StatCard({ label, value, color }) {
  return (
    <div style={{ background: C.paper, border: `1px solid ${C.line}`, borderRadius: C.r, padding: '17px 20px', boxShadow: C.shadowSm }}>
      <div style={{ fontSize: '.72rem', color: C.ink2, textTransform: 'uppercase', letterSpacing: '.07em', fontWeight: 500, marginBottom: 6 }}>{label}</div>
      <div style={{ fontFamily: C.font, fontSize: '2rem', fontWeight: 800, color }}>{value}</div>
    </div>
  )
}

/* ── Filter bar ── */
export function Filters({ options, value, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginBottom: 16 }}>
      {options.map(o => (
        <button key={o.value} onClick={() => onChange(o.value)}
          style={{
            padding: '4px 12px', borderRadius: 99, fontSize: '.78rem', fontWeight: 500,
            cursor: 'pointer', transition: 'all .12s', fontFamily: "'DM Sans',sans-serif",
            border: `1px solid ${value === o.value ? o.color || C.ink : C.line}`,
            background: value === o.value ? o.color || C.ink : C.paper,
            color: value === o.value ? '#fff' : C.ink2,
          }}>
          {o.label}
        </button>
      ))}
    </div>
  )
}

/* ── Avatar ── */
export function Ava({ user, size = 28 }) {
  const adm = user?.role === 'admin' || user?.is_superuser
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      background: adm ? C.adm : C.acc, color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * .32 + 'px', fontWeight: 700, flexShrink: 0, overflow: 'hidden',
    }}>
      {user?.avatar
        ? <img src={user.avatar} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }}/>
        : (user?.username?.[0] || '?').toUpperCase()}
    </div>
  )
}

/* ── File type pill ── */
export function FilePill({ name }) {
  const ext = (name || '').split('.').pop().toUpperCase()
  const isPdf = ext === 'PDF'
  const isImg = ['JPG', 'JPEG', 'PNG', 'GIF', 'WEBP'].includes(ext)
  return (
    <span style={{
      fontSize: '.67rem', fontWeight: 700, padding: '2px 5px', borderRadius: 3,
      flexShrink: 0, letterSpacing: '.03em',
      background: isPdf ? C.noBg : isImg ? C.okBg : C.smoke,
      color:      isPdf ? C.no   : isImg ? C.ok   : C.ink2,
    }}>
      {ext || 'FILE'}
    </span>
  )
}

/* ── Icons ── */
export function IcoSearch() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  )
}
export function IcoChevron({ open }) {
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
      style={{ transition: 'transform .18s', transform: open ? 'rotate(180deg)' : 'none', color: C.ink2, flexShrink: 0 }}>
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  )
}
