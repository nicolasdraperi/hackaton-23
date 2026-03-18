import { useState } from 'react'
import C from '../styles/tokens'

/* ── Field wrapper ── */
export function Field({ label, hint, error, children, style }) {
  return (
    <div style={{ marginBottom: 14, ...style }}>
      {label && (
        <label style={{ display: 'block', fontSize: '.82rem', fontWeight: 500, marginBottom: 4 }}>
          {label}
        </label>
      )}
      {children}
      {(hint || error) && (
        <p style={{ fontSize: '.75rem', marginTop: 3, color: error ? C.no : C.ink2 }}>
          {error || hint}
        </p>
      )}
    </div>
  )
}

function inputStyle(focused, error) {
  return {
    width: '100%', padding: '8px 12px',
    border: `1px solid ${error ? C.no : focused ? C.acc : C.line}`,
    borderRadius: C.rSm, fontSize: '.875rem',
    background: '#fff', color: C.ink, outline: 'none',
    boxShadow: focused ? `0 0 0 3px ${error ? 'rgba(192,25,15,.1)' : 'rgba(26,86,219,.1)'}` : 'none',
    transition: 'border-color .12s, box-shadow .12s',
  }
}

/* ── Input ── */
export function Input({ label, hint, error, containerStyle, style, ...props }) {
  const [focused, setFocused] = useState(false)
  return (
    <Field label={label} hint={hint} error={error} style={containerStyle}>
      <input
        {...props}
        onFocus={e => { setFocused(true); props.onFocus?.(e) }}
        onBlur={e  => { setFocused(false); props.onBlur?.(e) }}
        style={{ ...inputStyle(focused, error), ...style }}
      />
    </Field>
  )
}

/* ── Textarea ── */
export function Textarea({ label, hint, rows = 3, style, ...props }) {
  const [focused, setFocused] = useState(false)
  return (
    <Field label={label} hint={hint}>
      <textarea
        {...props}
        rows={rows}
        onFocus={e => { setFocused(true); props.onFocus?.(e) }}
        onBlur={e  => { setFocused(false); props.onBlur?.(e) }}
        style={{ ...inputStyle(focused, false), resize: 'vertical', fontFamily: "'DM Sans',sans-serif", ...style }}
      />
    </Field>
  )
}

/* ── Select ── */
export function Select({ label, hint, children, style, ...props }) {
  return (
    <Field label={label} hint={hint}>
      <select
        {...props}
        style={{
          width: '100%', padding: '8px 28px 8px 12px',
          border: `1px solid ${C.line}`, borderRadius: C.rSm,
          fontSize: '.875rem', background: '#fff', color: C.ink,
          outline: 'none', appearance: 'none', cursor: 'pointer',
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='7' viewBox='0 0 12 8'%3E%3Cpath fill='%2352525e' d='M6 8L0 0h12z'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat', backgroundPosition: 'right 10px center',
          ...style,
        }}>
        {children}
      </select>
    </Field>
  )
}

/* ── Alert ── */
const ALERT_MAP = {
  success: { bg: C.okBg,   color: C.ok,   border: C.okBorder   },
  error:   { bg: C.noBg,   color: C.no,   border: C.noBorder   },
  warning: { bg: C.waitBg, color: C.wait, border: C.waitBorder },
  info:    { bg: C.admBg,  color: C.adm,  border: '#c9c1ef'    },
}
export function Alert({ type = 'info', children, onClose }) {
  const s = ALERT_MAP[type]
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8,
      padding: '9px 13px', borderRadius: C.rSm, fontSize: '.875rem', marginBottom: 12,
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      <span>{children}</span>
      {onClose && (
        <button onClick={onClose}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', fontSize: '1rem', lineHeight: 1, padding: 0, opacity: .7 }}>
          ×
        </button>
      )}
    </div>
  )
}
