import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import api from '../api/axios.js'

const Trainings = () => {
  const { user } = useAuth()
  const [trainings, setTrainings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    duration_days: 1,
    is_active: true,
  })

  useEffect(() => {
    fetchTrainings()
  }, [])

  const fetchTrainings = async () => {
    try {
      const response = await api.get('/users/trainings/')
      setTrainings(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching trainings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setFormData({
      ...formData,
      [e.target.name]: value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/users/trainings/', formData)
      setShowModal(false)
      fetchTrainings()
      setFormData({
        name: '',
        description: '',
        start_date: '',
        end_date: '',
        duration_days: 1,
        is_active: true,
      })
    } catch (error) {
      console.error('Error creating training:', error)
      alert('Error creating training')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this training?')) {
      try {
        await api.delete(`/users/trainings/${id}/`)
        fetchTrainings()
      } catch (error) {
        console.error('Error deleting training:', error)
        alert('Error deleting training')
      }
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1>Trainings</h1>
        {user?.role === 'manager' && (
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            Create Training
          </button>
        )}
      </div>

      <div className="grid grid-2">
        {trainings.map((training) => (
          <div key={training.id} className="card">
            <div className="flex-between" style={{ marginBottom: '1rem' }}>
              <h3>{training.name}</h3>
              <span className={`badge ${training.is_active ? 'badge-success' : 'badge-danger'}`}>
                {training.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <p className="text-secondary text-sm" style={{ marginBottom: '1rem' }}>
              {training.description?.substring(0, 100)}...
            </p>
            <div style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              <div>Start: {training.start_date}</div>
              <div>End: {training.end_date}</div>
              <div>Duration: {training.duration_days} days</div>
              <div>Trainer: {training.assigned_trainer_name || 'Not assigned'}</div>
              <div>Modules: {training.module_count || 0}</div>
            </div>
            <div className="flex gap-1">
              <Link to={`/trainings/${training.id}`} className="btn btn-primary btn-sm">
                View Details
              </Link>
              {user?.role === 'manager' && (
                <button
                  onClick={() => handleDelete(training.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {trainings.length === 0 && (
        <div className="card text-center">
          <p>No trainings found.</p>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create Training</h2>
              <button onClick={() => setShowModal(false)} className="modal-close">
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  name="name"
                  className="form-control"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description *</label>
                <textarea
                  name="description"
                  className="form-control"
                  value={formData.description}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Start Date *</label>
                  <input
                    type="date"
                    name="start_date"
                    className="form-control"
                    value={formData.start_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">End Date *</label>
                  <input
                    type="date"
                    name="end_date"
                    className="form-control"
                    value={formData.end_date}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Duration (days) *</label>
                <input
                  type="number"
                  name="duration_days"
                  className="form-control"
                  value={formData.duration_days}
                  onChange={handleChange}
                  required
                  min="1"
                />
              </div>

              <div className="form-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                  Active
                </label>
              </div>

              <div className="flex gap-1">
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-outline"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Trainings
