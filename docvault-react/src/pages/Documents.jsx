import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import C from '../styles/tokens'
import api from '../api'
import { Btn } from '../components/primitives'
import { Field, Select, Alert } from '../components/forms'
import { Card, Page, PageHead, Filters } from '../components/layout'
import DropZone from '../components/DropZone'
import BatchCard from '../components/BatchCard'
import { Spinner } from '../components/primitives'

/* ── Upload (user + admin) ── */
export function Upload({ adminMode = false, users = [] }) {
  const navigate = useNavigate()
  const [label,   setLabel]  = useState('')
  const [files,   setFiles]  = useState([])
  const [userId,  setUserId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error,   setError]  = useState('')

  const submit = async e => {
    e.preventDefault()
    if (!files.length) { setError('Veuillez selectionner au moins un fichier.'); return }
    setLoading(true); setError('')
    try {
      const fd = new FormData()
      if (label) fd.append('label', label)
      files.forEach(f => fd.append('documents', f))
      if (adminMode && userId) fd.append('user_id', userId)
      await (adminMode ? api.adminUpload(fd) : api.uploadBatch(fd))
      navigate(adminMode ? '/admin/review' : '/documents')
    } catch (ex) {
      setError(ex.data?.detail || "Une erreur est survenue lors de l'upload.")
    } finally { setLoading(false) }
  }

  return (
    <Page>
      <PageHead
        title={adminMode ? 'Upload de documents' : 'Uploader des documents'}
        sub={adminMode ? "Uploadez des documents pour n'importe quel utilisateur" : 'Selectionnez plusieurs fichiers PDF ou images'}
      />
      <div style={{ maxWidth: 680 }}>
        <Card>
          <div style={{ padding: '1.5rem' }}>
            {error && <Alert type="error" onClose={() => setError('')}>{error}</Alert>}
            <form onSubmit={submit}>
              {adminMode && users.length > 0 && (
                <Select label="Utilisateur cible" value={userId} onChange={e => setUserId(e.target.value)} hint="Laissez vide pour uploader en votre nom.">
                  <option value="">Moi-meme</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.username} (@{u.username})
                    </option>
                  ))}
                </Select>
              )}
              <Field label={<>Nom du lot <span style={{ color: C.ink2, fontWeight: 400 }}>(optionnel)</span></>}>
                <input
                  value={label} onChange={e => setLabel(e.target.value)}
                  placeholder="Ex: Justificatifs mars 2026..."
                  style={{ width: '100%', padding: '8px 12px', border: `1px solid ${C.line}`, borderRadius: C.rSm, fontSize: '.875rem', background: '#fff', color: C.ink, outline: 'none' }}
                />
              </Field>
              <Field label="Fichiers">
                <DropZone files={files} onChange={setFiles}/>
              </Field>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
                <span style={{ fontSize: '.82rem', color: C.ink2 }}>
                  {files.length === 0
                    ? 'Aucun fichier selectionne'
                    : `${files.length} fichier${files.length > 1 ? 's' : ''} selectionne${files.length > 1 ? 's' : ''}`}
                </span>
                <Btn type="submit" variant="accent" loading={loading} disabled={!files.length}>
                  Envoyer les documents
                </Btn>
              </div>
            </form>
          </div>
        </Card>
      </div>
    </Page>
  )
}

/* ── MyDocuments ── */
const FILTERS = [
  { value: '',         label: 'Tous'       },
  { value: 'pending',  label: 'En attente', color: C.wait },
  { value: 'approved', label: 'Approuves',  color: C.ok   },
  { value: 'rejected', label: 'Refuses',    color: C.no   },
]

export function MyDocuments() {
  const navigate = useNavigate()
  const [batches, setBatches] = useState([])
  const [status,  setStatus]  = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.getBatches(status)
      .then(d => setBatches(Array.isArray(d) ? d : d?.results || []))
      .catch(() => setBatches([]))
      .finally(() => setLoading(false))
  }, [status])

  return (
    <Page>
      <PageHead
        title="Mes Documents"
        sub="Vos lots d'envoi et leur statut de validation"
        action={<Btn variant="accent" onClick={() => navigate('/upload')}>Nouvel upload</Btn>}
      />
      <Filters options={FILTERS} value={status} onChange={setStatus}/>
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}><Spinner size={28}/></div>
      ) : batches.length > 0 ? (
        batches.map(b => <BatchCard key={b.id} batch={b}/>)
      ) : (
        <Card style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ fontWeight: 600, color: C.ink, marginBottom: 6 }}>Aucun document trouve</p>
          <p style={{ fontSize: '.85rem', color: C.ink2, marginBottom: '1rem' }}>
            {status ? 'Aucun lot avec ce statut.' : "Vous n'avez pas encore uploade de documents."}
          </p>
          <Btn variant="accent" onClick={() => navigate('/upload')}>Uploader maintenant</Btn>
        </Card>
      )}
    </Page>
  )
}
