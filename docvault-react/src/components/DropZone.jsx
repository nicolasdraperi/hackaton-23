import { useState, useRef } from 'react'
import C from '../styles/tokens'
import { FilePill } from './layout'

const ACCEPT = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'image/webp']

function fmtSize(b) {
  return b < 1048576 ? (b / 1024).toFixed(1) + ' Ko' : (b / 1048576).toFixed(1) + ' Mo'
}

export default function DropZone({ files, onChange }) {
  const [drag, setDrag] = useState(false)
  const inputRef = useRef()

  const addFiles = (incoming) => {
    const merged = [...files]
    incoming
      .filter(f => ACCEPT.includes(f.type))
      .forEach(f => {
        if (!merged.some(x => x.name === f.name && x.size === f.size)) merged.push(f)
      })
    onChange(merged)
  }

  const remove = (i) => onChange(files.filter((_, idx) => idx !== i))

  return (
    <div>
      <div
        onClick={() => inputRef.current.click()}
        onDragOver={e  => { e.preventDefault(); setDrag(true)  }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); addFiles(Array.from(e.dataTransfer.files)) }}
        style={{
          border: `2px dashed ${drag ? C.acc : C.line}`,
          borderRadius: C.r, padding: '2.5rem 1.5rem',
          textAlign: 'center', cursor: 'pointer', transition: 'all .15s',
          background: drag ? C.accSoft : '#fff',
        }}>
        <input
          ref={inputRef}
          type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.gif,.webp"
          style={{ display: 'none' }}
          onChange={e => { addFiles(Array.from(e.target.files)); e.target.value = '' }}
        />
        <p style={{ fontWeight: 600, color: C.ink, marginBottom: 4, fontSize: '.95rem' }}>
          Glissez vos fichiers ici
        </p>
        <p style={{ fontSize: '.82rem', color: C.ink2 }}>
          ou cliquez pour parcourir — PDF, JPG, PNG, WEBP acceptes
        </p>
      </div>

      {files.length > 0 && (
        <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 5 }}>
          {files.map((f, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 8, padding: '7px 11px',
              background: '#fff', border: `1px solid ${C.line}`, borderRadius: C.rSm,
            }}>
              <FilePill name={f.name}/>
              <span style={{ flex: 1, fontWeight: 500, fontSize: '.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {f.name}
              </span>
              <span style={{ fontSize: '.75rem', color: C.ink2, flexShrink: 0 }}>{fmtSize(f.size)}</span>
              <button
                onClick={() => remove(i)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: C.ink2, padding: '2px 4px', borderRadius: 3, fontSize: '.85rem', lineHeight: 1 }}
                onMouseEnter={e => { e.target.style.background = C.noBg;  e.target.style.color = C.no   }}
                onMouseLeave={e => { e.target.style.background = 'none';   e.target.style.color = C.ink2 }}>
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
