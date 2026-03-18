import { useState, useEffect } from 'react'
import api from '../api'

export default function useBatches(defaultStatus = '') {
  const [batches, setBatches] = useState([])
  const [stats,   setStats]   = useState({})
  const [status,  setStatus]  = useState(defaultStatus)
  const [ufilter, setUfilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [rejectTarget, setRejectTarget] = useState(null)

  const load = () => {
    setLoading(true)
    api.adminBatches(status, ufilter)
      .then(d => {
        setBatches(Array.isArray(d) ? d : d?.results || [])
        setStats(d?.stats || {})
      })
      .catch(() => setBatches([]))
      .finally(() => setLoading(false))
  }

  useEffect(load, [status, ufilter])

  const approve = async (id) => { await api.approve(id).catch(() => {}); load() }
  const reject  = async (id, reason) => {
    await api.reject(id, reason).catch(() => {})
    setRejectTarget(null)
    load()
  }

  return {
    batches, stats,
    status,  setStatus,
    ufilter, setUfilter,
    loading,
    rejectTarget, setRejectTarget,
    approve, reject,
  }
}
