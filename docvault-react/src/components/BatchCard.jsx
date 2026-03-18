import { useState } from 'react'
import C from '../styles/tokens'
import { Badge, Btn } from './primitives'
import { FilePill, IcoChevron } from './layout'
import api from '../api'

const STATUS_LABEL = { pending: 'En attente', approved: 'Approuve', rejected: 'Refuse' }

export default function BatchCard({ batch, admin = false, onApprove, onReject }) {
  const [open, setOpen] = useState(batch.status === 'pending' || batch.status === 'rejected')
  const label = batch.label || `Lot #${batch.id}`
  const date  = new Date(batch.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })

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
            {admin && batch.user && <><strong>@{batch.user.username}</strong> · </>}
            {date} · {batch.documents?.length || 0} fichier{batch.documents?.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Badge status={batch.status}>{STATUS_LABEL[batch.status]}</Badge>
          {batch.reviewed_by && (
            <span style={{ fontSize: '.72rem', color: C.ink2 }}>par {batch.reviewed_by.username}</span>
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
          {batch.documents?.map(doc => (
            <div key={doc.id} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '9px 18px', borderBottom: `1px solid ${C.line}`, fontSize: '.85rem' }}>
              <FilePill name={doc.original_name}/>
              <span style={{ flex: 1, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {doc.original_name}
              </span>
              <span style={{ fontSize: '.75rem', color: C.ink2, flexShrink: 0 }}>{doc.file_size_kb} Ko</span>
              <a
                href={api.viewDoc(doc.id)} target="_blank" rel="noreferrer"
                style={{ fontSize: '.78rem', color: C.acc, fontWeight: 500, padding: '3px 7px', borderRadius: 4, transition: 'background .12s', flexShrink: 0 }}
                onMouseEnter={e => e.target.style.background = C.accSoft}
                onMouseLeave={e => e.target.style.background = 'transparent'}>
                Voir
              </a>
            </div>
          ))}

          {/* Admin actions */}
          {admin && (
            <div style={{ padding: '11px 18px', display: 'flex', gap: 7 }}>
              {batch.status !== 'approved' && (
                <Btn variant="success" size="sm" onClick={() => onApprove(batch.id)}>Approuver le lot</Btn>
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
