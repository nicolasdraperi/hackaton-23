import { useState } from 'react'
import C from '../styles/tokens'
import { Badge, Btn } from './primitives'
import { FilePill, IcoChevron } from './layout'
import api from '../api'

const STATUS_LABEL = { pending: 'En attente', approved: 'Approuve', rejected: 'Refuse' }

// Composant affichant les résultats OCR d'un document
function OcrPanel({ ocr }) {
  if (!ocr) return null

  const fields = Object.entries(ocr).filter(([key]) =>
    !['document_type', 'missing_fields', 'confidence_fields'].includes(key)
  )

  return (
    <div style={{
      margin: '8px 18px 12px',
      border: `1px solid ${C.line}`,
      borderRadius: C.rSm,
      overflow: 'hidden',
      fontSize: '.8rem',
    }}>
      {/* En-tête OCR */}
      <div style={{
        background: C.admBg,
        padding: '6px 12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 8,
      }}>
        <span style={{ fontWeight: 600, color: C.adm }}>
          Résultats OCR — {ocr.document_type || 'inconnu'}
        </span>
        {ocr.confidence_fields != null && (
          <span style={{ color: C.ink2, fontSize: '.75rem' }}>
            Confiance globale : {(ocr.confidence_fields * 100).toFixed(1)}%
          </span>
        )}
      </div>

      {/* Champs extraits */}
      <div style={{ padding: '8px 0' }}>
        {fields.map(([key, val]) => {
          if (typeof val !== 'object' || val === null) return null
          const isOk = val.valid === true
          const isMissing = val.missing === true
          return (
            <div key={key} style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 8,
              padding: '5px 12px',
              borderBottom: `1px solid ${C.line}`,
            }}>
              {/* Indicateur statut */}
              <span style={{
                width: 8, height: 8, borderRadius: '50%', flexShrink: 0, marginTop: 4,
                background: isMissing ? C.no : isOk ? C.ok : C.wait,
              }}/>
              {/* Nom du champ */}
              <span style={{ width: 160, flexShrink: 0, color: C.ink2, fontWeight: 500 }}>
                {key.replace(/_/g, ' ')}
              </span>
              {/* Valeur */}
              <span style={{
                flex: 1,
                color: isMissing ? C.no : C.ink,
                fontFamily: val.value ? 'Courier New, monospace' : 'inherit',
              }}>
                {isMissing ? 'manquant' : (val.value ?? '—')}
              </span>
              {/* Confiance */}
              {val.confidence != null && (
                <span style={{ color: C.ink2, flexShrink: 0, fontSize: '.75rem' }}>
                  {(val.confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
          )
        })}
      </div>

      {/* Champs manquants */}
      {ocr.missing_fields?.length > 0 && (
        <div style={{
          padding: '6px 12px',
          background: C.noBg,
          color: C.no,
          fontSize: '.78rem',
        }}>
          Champs manquants : {ocr.missing_fields.join(', ')}
        </div>
      )}
    </div>
  )
}

export default function BatchCard({ batch, admin = false, onApprove, onReject }) {
  const [open, setOpen] = useState(batch.status === 'pending' || batch.status === 'rejected')
  // FIX 2 — état OCR par document (clé = index du document)
  const [ocrOpen, setOcrOpen] = useState({})

  const label = batch.label || `Lot #${batch._id}`
  const date  = new Date(batch.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })

  const toggleOcr = (index) => {
    setOcrOpen(prev => ({ ...prev, [index]: !prev[index] }))
  }

  return (
    <div style={{ background: C.paper, border: `1px solid ${C.line}`, borderRadius: C.r, marginBottom: 10, boxShadow: C.shadowSm, overflow: 'hidden' }}>

      {/* Header */}
      <div
        onClick={() => setOpen(o => !o)}
        style={{ padding: '12px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, cursor: 'pointer', transition: 'background .12s' }}
        onMouseEnter={e => e.currentTarget.style.background = C.smoke}
        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
        <div>
          <div style={{ fontWeight: 600, fontSize: '.9rem' }}>{label}</div>
          <div style={{ fontSize: '.78rem', color: C.ink2, marginTop: 2 }}>
            {admin && batch.user_id && <><strong>user #{batch.user_id}</strong> · </>}
            {date} · {batch.documents?.length || 0} fichier{batch.documents?.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Badge status={batch.status}>{STATUS_LABEL[batch.status]}</Badge>
          {batch.reviewed_by && (
            <span style={{ fontSize: '.72rem', color: C.ink2 }}>par {batch.reviewed_by}</span>
          )}
          <IcoChevron open={open}/>
        </div>
      </div>

      {/* Rejection note */}
      {batch.status === 'rejected' && batch.rejection_reason && (
        <div style={{ margin: '0 18px 10px', padding: '7px 12px', background: C.noBg, borderLeft: `3px solid ${C.no}`, borderRadius: '0 4px 4px 0', fontSize: '.82rem', color: C.no }}>
          <div style={{ fontSize: '.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 3 }}>
            Motif de refus
          </div>
          {batch.rejection_reason}
        </div>
      )}

      {/* Documents list */}
      {open && (
        <div style={{ borderTop: `1px solid ${C.line}` }}>
          {batch.documents?.map((doc, index) => (
            <div key={index}>
              {/* Ligne document */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '9px 18px', borderBottom: `1px solid ${C.line}`, fontSize: '.85rem' }}>
                <FilePill name={doc.original_name}/>
                <span style={{ flex: 1, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {doc.original_name}
                </span>
                <span style={{ fontSize: '.75rem', color: C.ink2, flexShrink: 0 }}>
                  {doc.size_kb} Ko
                </span>

                {/* FIX 2 — bouton OCR si données disponibles */}
                {doc.ocr_data && (
                  <Btn
                    variant={ocrOpen[index] ? 'accent' : 'outline'}
                    size="sm"
                    onClick={() => toggleOcr(index)}>
                    {ocrOpen[index] ? 'Masquer OCR' : 'OCR'}
                  </Btn>
                )}

                <a
                  href={api.viewDoc(batch._id, index)} target="_blank" rel="noreferrer"
                  style={{ fontSize: '.78rem', color: C.acc, fontWeight: 500, padding: '3px 7px', borderRadius: 4, transition: 'background .12s', flexShrink: 0 }}
                  onMouseEnter={e => e.target.style.background = C.accSoft}
                  onMouseLeave={e => e.target.style.background = 'transparent'}>
                  Télécharger
                </a>
              </div>

              {/* FIX 2 — panneau OCR dépliable par document */}
              {ocrOpen[index] && doc.ocr_data && (
                <OcrPanel ocr={doc.ocr_data}/>
              )}
            </div>
          ))}

          {/* Admin actions */}
          {admin && (
            <div style={{ padding: '11px 18px', display: 'flex', gap: 7 }}>
              {batch.status !== 'approved' && (
                <Btn variant="success" size="sm" onClick={() => onApprove(batch._id)}>Approuver le lot</Btn>
              )}
              {batch.status !== 'rejected' && (
                <Btn variant="danger" size="sm" onClick={() => onReject(batch)}>Refuser le lot</Btn>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
