import { useState } from 'react'
import C from '../styles/tokens'

/* ── Spinner ── */
export function Spinner({ size = 20, style }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      style={{ animation: 'spin .7s linear infinite', flexShrink: 0, ...style }}>
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2.5" strokeOpacity=".2"/>
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
    </svg>
  )
}

/* ── Badge ── */
const BADGE_MAP = {
  pending:  { bg: C.waitBg, color: C.wait, border: C.waitBorder },
  approved: { bg: C.okBg,   color: C.ok,   border: C.okBorder   },
  rejected: { bg: C.noBg,   color: C.no,   border: C.noBorder   },
  admin:    { bg: C.admBg,  color: C.adm,  border: '#c9c1ef'    },
  user:     { bg: C.smoke,  color: C.ink2, border: C.line        },
}
export function Badge({ status, children }) {
  const s = BADGE_MAP[status] || BADGE_MAP.user
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      fontSize: '.72rem', fontWeight: 500, padding: '3px 9px',
      borderRadius: 99, whiteSpace: 'nowrap',
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor', flexShrink: 0 }}/>
      {children}
    </span>
  )
}

/* ── Btn ── */
const VARIANTS = {
  primary: { bg: C.ink,        fg: '#fff', hbg: '#1e1e2e'    },
  accent:  { bg: C.acc,        fg: '#fff', hbg: C.accHover   },
  success: { bg: C.ok,         fg: '#fff', hbg: '#086645'    },
  danger:  { bg: C.no,         fg: '#fff', hbg: '#9e1309'    },
  outline: { bg: 'transparent', fg: C.ink,  hbg: C.smoke, border: `1px solid ${C.line}` },
  ghost:   { bg: 'transparent', fg: C.ink2, hbg: C.smoke, border: '1px solid transparent' },
}
const SIZES = {
  md: { fontSize: '.85rem', padding: '8px 16px' },
  sm: { fontSize: '.78rem', padding: '5px 11px' },
}
export function Btn({ variant = 'primary', size = 'md', loading, style, children, ...props }) {
  const [hovered, setHovered] = useState(false)
  const v = VARIANTS[variant]
  return (
    <button
      {...props}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        fontFamily: C.font, fontWeight: 500, borderRadius: C.rSm,
        border: 'none', cursor: 'pointer', transition: 'all .12s',
        whiteSpace: 'nowrap', lineHeight: 1.3, textDecoration: 'none',
        ...SIZES[size],
        background: hovered ? v.hbg : v.bg,
        color: v.fg,
        ...(v.border ? { border: v.border } : {}),
        ...(props.disabled || loading ? { opacity: .5, cursor: 'not-allowed' } : {}),
        ...style,
      }}>
      {loading ? <Spinner size={14}/> : children}
    </button>
  )
}
