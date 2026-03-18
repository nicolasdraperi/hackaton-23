import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import C from '../styles/tokens'
import api from '../api'
import useBatches from '../hooks/useBatches'
import { Btn, Spinner } from '../components/primitives'
import { Textarea } from '../components/forms'
import { Card, CardHeader, Page, PageHead, StatCard, Filters, Modal, IcoSearch } from '../components/layout'
import BatchCard from '../components/BatchCard'
import { Upload } from './Documents'

/* ── Shared reject modal ── */
function RejectModal({ target, onClose, onConfirm }) {
  const [reason,  setReason]  = useState('')
  const [loading, setLoading] = useState(false)
  useEffect(() => { if (!target) setReason('') }, [target])

  const confirm = async () => {
    setLoading(true)
    await onConfirm(target.id, reason)
    setLoading(false)
  }

  return (
    <Modal open={!!target} onClose={onClose} title="Refuser le lot">
      <p style={{ fontSize: '.85rem', color: C.ink2, marginBottom: '1rem' }}>
        {target?.label || `Lot #${target?.id}`}
      </p>
      <Textarea
        label="Motif de refus (visible par l'utilisateur)"
        value={reason}
        onChange={e => setReason(e.target.value)}
        placeholder="Ex: Document illisible, format incorrect..."
        rows={4}
      />
      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 4 }}>
        <Btn variant="outline" onClick={onClose}>Annuler</Btn>
        <Btn variant="danger" loading={loading} onClick={confirm}>Confirmer le refus</Btn>
      </div>
    </Modal>
  )
}

/* ── Admin Dashboard ── */
export function AdminDashboard() {
  const navigate = useNavigate()
  const { batches, stats, loading, rejectTarget, setRejectTarget, approve, reject } = useBatches('pending')

  return (
    <Page>
      <PageHead title="Tableau de bord" sub="Vue d'ensemble de l'activite DocVault"/>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))', gap: 14, marginBottom: '1.75rem' }}>
        <StatCard label="Lots en attente" value={stats.pending  ?? batches.length} color={C.wait}/>
        <StatCard label="Lots approuves"  value={stats.approved ?? '—'}            color={C.ok}/>
        <StatCard label="Lots refuses"    value={stats.rejected ?? '—'}            color={C.no}/>
        <StatCard label="Utilisateurs"    value={stats.users    ?? '—'}            color={C.acc}/>
      </div>
      <Card>
        <CardHeader
          title="Lots en attente de validation"
          action={<Btn variant="outline" size="sm" onClick={() => navigate('/admin/review')}>Voir tout</Btn>}
        />
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '2.5rem' }}><Spinner size={26}/></div>
        ) : batches.length > 0 ? (
          <div style={{ padding: '16px 20px' }}>
            {batches.slice(0, 8).map(b => (
              <BatchCard key={b.id} batch={b} admin onApprove={approve} onReject={setRejectTarget}/>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: C.ink2 }}>
            <p style={{ fontWeight: 600, color: C.ink, marginBottom: 4 }}>Aucun lot en attente</p>
            <p style={{ fontSize: '.85rem' }}>Tous les lots ont ete traites.</p>
          </div>
        )}
      </Card>
      <RejectModal target={rejectTarget} onClose={() => setRejectTarget(null)} onConfirm={reject}/>
    </Page>
  )
}

/* ── Admin Review ── */
const FILTERS = [
  { value: 'pending',  label: 'En attente', color: C.wait },
  { value: 'approved', label: 'Approuves',  color: C.ok   },
  { value: 'rejected', label: 'Refuses',    color: C.no   },
  { value: '',         label: 'Tous'        },
]

export function AdminReview() {
  const { batches, status, setStatus, ufilter, setUfilter, loading, rejectTarget, setRejectTarget, approve, reject } = useBatches('pending')

  return (
    <Page>
      <PageHead title="Revision des lots" sub="Approuvez ou refusez les lots de documents soumis"/>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginBottom: 20 }}>
        <Filters options={FILTERS} value={status} onChange={setStatus}/>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 7, alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: C.ink2, pointerEvents: 'none' }}>
              <IcoSearch/>
            </span>
            <input
              value={ufilter}
              onChange={e => setUfilter(e.target.value)}
              placeholder="Filtrer par utilisateur..."
              style={{ padding: '7px 12px 7px 30px', border: `1px solid ${C.line}`, borderRadius: C.rSm, fontSize: '.875rem', background: '#fff', color: C.ink, outline: 'none', width: 220 }}
            />
          </div>
          {ufilter && <Btn variant="ghost" size="sm" onClick={() => setUfilter('')}>Effacer</Btn>}
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}><Spinner size={28}/></div>
      ) : batches.length > 0 ? (
        batches.map(b => <BatchCard key={b.id} batch={b} admin onApprove={approve} onReject={setRejectTarget}/>)
      ) : (
        <Card style={{ textAlign: 'center', padding: '3rem', color: C.ink2 }}>
          <p style={{ fontWeight: 600, color: C.ink, marginBottom: 4 }}>Aucun lot trouve</p>
          <p style={{ fontSize: '.85rem' }}>Modifiez les filtres pour afficher plus de resultats.</p>
        </Card>
      )}
      <RejectModal target={rejectTarget} onClose={() => setRejectTarget(null)} onConfirm={reject}/>
    </Page>
  )
}

/* ── Admin Upload ── */
export function AdminUpload() {
  const [users,   setUsers]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getUsers()
      .then(d => setUsers(Array.isArray(d) ? d : d?.results || []))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <Spinner size={28}/>
    </div>
  )
  return <Upload adminMode users={users}/>
}

/* ── Admin Users ── */
export function AdminUsers() {
  const [users,       setUsers]       = useState([])
  const [query,       setQuery]       = useState('')
  const [loading,     setLoading]     = useState(true)
  const [roleTarget,  setRoleTarget]  = useState(null)
  const [selectedRole, setSelectedRole] = useState('')
  const [acting,      setActing]      = useState(false)

  const load = (q = query) => {
    setLoading(true)
    api.getUsers(q)
      .then(d => setUsers(Array.isArray(d) ? d : d?.results || []))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false))
  }
  useEffect(() => load(''), [])

  const openRole = (u) => { setRoleTarget(u); setSelectedRole(u.role) }
  const saveRole = async () => {
    setActing(true)
    try {
      await api.changeRole(roleTarget.id, selectedRole)
      setUsers(us => us.map(u => u.id === roleTarget.id ? { ...u, role: selectedRole } : u))
      setRoleTarget(null)
    } catch {}
    setActing(false)
  }

  return (
    <Page>
      <PageHead title="Gestion des utilisateurs" sub="Gerez les roles et acces de tous les membres"/>

      <div style={{ display: 'flex', gap: 8, marginBottom: 20, maxWidth: 420 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <span style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: C.ink2, pointerEvents: 'none' }}>
            <IcoSearch/>
          </span>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && load(query)}
            placeholder="Rechercher par nom ou email..."
            style={{ width: '100%', padding: '7px 12px 7px 30px', border: `1px solid ${C.line}`, borderRadius: C.rSm, fontSize: '.875rem', background: '#fff', color: C.ink, outline: 'none' }}
          />
        </div>
        <Btn variant="outline" size="sm" onClick={() => load(query)}>Rechercher</Btn>
        {query && <Btn variant="ghost" size="sm" onClick={() => { setQuery(''); load('') }}>Effacer</Btn>}
      </div>

      <Card style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}><Spinner size={26}/></div>
        ) : users.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.85rem' }}>
              <thead>
                <tr>
                  {['Utilisateur', 'Email', 'Role', 'Membre depuis', 'Lots', 'Action'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '10px 16px', fontSize: '.72rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: C.ink2, borderBottom: `2px solid ${C.line}`, whiteSpace: 'nowrap' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.map(u => {
                  const adm = u.role === 'admin' || u.is_superuser
                  const fullName = u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : null
                  return (
                    <tr key={u.id} style={{ borderBottom: `1px solid ${C.line}` }}
                      onMouseEnter={e => e.currentTarget.querySelectorAll('td').forEach(td => td.style.background = C.smoke)}
                      onMouseLeave={e => e.currentTarget.querySelectorAll('td').forEach(td => td.style.background = 'transparent')}>
                      <td style={{ padding: '12px 16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                          <div style={{ width: 32, height: 32, borderRadius: '50%', background: adm ? C.adm : C.acc, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '.78rem', fontWeight: 700, flexShrink: 0 }}>
                            {(u.username?.[0] || '?').toUpperCase()}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600 }}>{fullName || u.username}</div>
                            <div style={{ fontSize: '.75rem', color: C.ink2 }}>@{u.username}</div>
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '12px 16px', color: C.ink2 }}>{u.email || '—'}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: '.72rem', fontWeight: 500, padding: '3px 9px', borderRadius: 99, background: adm ? C.admBg : C.smoke, color: adm ? C.adm : C.ink2, border: `1px solid ${adm ? '#c9c1ef' : C.line}` }}>
                          <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor' }}/>
                          {adm ? 'Admin' : 'Utilisateur'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', color: C.ink2, whiteSpace: 'nowrap' }}>
                        {u.date_joined ? new Date(u.date_joined).toLocaleDateString('fr-FR') : '—'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>{u.batches_count ?? '—'}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <Btn variant="outline" size="sm" onClick={() => openRole(u)}>Modifier le role</Btn>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem', color: C.ink2 }}>
            <p style={{ fontWeight: 600, color: C.ink, marginBottom: 4 }}>Aucun utilisateur trouve</p>
          </div>
        )}
      </Card>

      <Modal open={!!roleTarget} onClose={() => setRoleTarget(null)} title="Modifier le role">
        <p style={{ fontSize: '.85rem', color: C.ink2, marginBottom: '1.25rem' }}>@{roleTarget?.username}</p>
        <div style={{ display: 'flex', gap: 10, marginBottom: 4 }}>
          {[
            { value: 'user',  label: 'Utilisateur',    sub: 'Upload et consultation' },
            { value: 'admin', label: 'Administrateur',  sub: 'Acces complet' },
          ].map(o => (
            <label key={o.value} style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, padding: '11px 13px', border: `1px solid ${selectedRole === o.value ? C.acc : C.line}`, borderRadius: C.rSm, cursor: 'pointer', background: selectedRole === o.value ? C.accSoft : 'transparent', transition: 'all .12s' }}>
              <input type="radio" name="role" value={o.value} checked={selectedRole === o.value} onChange={() => setSelectedRole(o.value)} style={{ accentColor: C.acc }}/>
              <div>
                <div style={{ fontWeight: 600, fontSize: '.875rem' }}>{o.label}</div>
                <div style={{ fontSize: '.75rem', color: C.ink2 }}>{o.sub}</div>
              </div>
            </label>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: '1.1rem' }}>
          <Btn variant="outline" onClick={() => setRoleTarget(null)}>Annuler</Btn>
          <Btn variant="primary" loading={acting} onClick={saveRole}>Enregistrer</Btn>
        </div>
      </Modal>
    </Page>
  )
}
