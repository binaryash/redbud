import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import api from '../api/axios.js'

const Modules = () => {
  const { user } = useAuth()
  const [modules, setModules] = useState([])
  const [trainings, setTrainings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    training: '',
    title: '',
    description: '',
    order: 0,
    duration_hours: '1.00',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [modulesRes, trainingsRes] = await Promise.all([
        api.get('/users/modules/'),
        api.get('/users/trainings/'),
      ])
      setModules(modulesRes.data.results || modulesRes.data)
      setTrainings(trainingsRes.data.results || trainingsRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/users/modules/', formData)
      setShowModal(false)
      fetchData()
      setFormData({
        training: '',
        title: '',
        description: '',
        order: 0,
        duration_hours: '1.00',
      })
    } catch (error) {
      console.error('Error creating module:', error)
      alert('Error creating module')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this module?')) {
      try {
        await api.delete(`/users/modules/${id}/`)
        fetchData()
      } catch (error) {
        console.error('Error deleting module:', error)
        alert('Error deleting module')
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
        <h1>Training Modules</h1>
        {(user?.role === 'manager' || user?.role === 'trainer') && (
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            Create Module
          </button>
        )}
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Training</th>
              <th>Duration (hrs)</th>
              <th>Order</th>
              <th>Created By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {modules.map((module) => (
              <tr key={module.id}>
                <td>{module.title}</td>
                <td>{module.training}</td>
                <td>{module.duration_hours}</td>
                <td>{module.order}</td>
                <td>{module.created_by_name}</td>
                <td>
                  {(user?.role === 'manager' || user?.role === 'trainer') && (
                    <button
                      onClick={() => handleDelete(module.id)}
                      className="btn btn-danger btn-sm"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {modules.length === 0 && (
          <p className="text-center" style={{ padding: '2rem' }}>No modules found.</p>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create Module</h2>
              <button onClick={() => setShowModal(false)} className="modal-close">
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Training *</label>
                <select
                  name="training"
                  className="form-control"
                  value={formData.training}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a training</option>
                  {trainings.map((training) => (
                    <option key={training.id} value={training.id}>
                      {training.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Title *</label>
                <input
                  type="text"
                  name="title"
                  className="form-control"
                  value={formData.title}
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
                  <label className="form-label">Order *</label>
                  <input
                    type="number"
                    name="order"
                    className="form-control"
                    value={formData.order}
                    onChange={handleChange}
                    required
                    min="0"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Duration (hours) *</label>
                  <input
                    type="number"
                    name="duration_hours"
                    className="form-control"
                    value={formData.duration_hours}
                    onChange={handleChange}
                    required
                    step="0.1"
                    min="0.1"
                  />
                </div>
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

export default Modules
