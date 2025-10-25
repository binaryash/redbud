import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/axios.js'

const TrainingDetail = () => {
  const { id } = useParams()
  const [training, setTraining] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTrainingDetail()
  }, [id])

  const fetchTrainingDetail = async () => {
    try {
      const response = await api.get(`/users/trainings/${id}/`)
      setTraining(response.data)
    } catch (error) {
      console.error('Error fetching training detail:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (!training) {
    return <div>Training not found</div>
  }

  return (
    <div>
      <Link to="/trainings" style={{ marginBottom: '1rem', display: 'inline-block' }}>
        ← Back to Trainings
      </Link>

      <div className="card">
        <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
          <h1>{training.name}</h1>
          <span className={`badge ${training.is_active ? 'badge-success' : 'badge-danger'}`}>
            {training.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Start Date
            </h3>
            <p>{training.start_date}</p>
          </div>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              End Date
            </h3>
            <p>{training.end_date}</p>
          </div>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Duration
            </h3>
            <p>{training.duration_days} days</p>
          </div>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Assigned Trainer
            </h3>
            <p>{training.assigned_trainer_name || 'Not assigned'}</p>
          </div>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Created By
            </h3>
            <p>{training.created_by_name}</p>
          </div>
          <div>
            <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Employees Enrolled
            </h3>
            <p>{training.employee_count}</p>
          </div>
        </div>

        <div>
          <h3 className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Description
          </h3>
          <p>{training.description}</p>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>Training Modules ({training.modules?.length || 0})</h2>
        {training.modules && training.modules.length > 0 ? (
          <div className="grid grid-2">
            {training.modules.map((module) => (
              <div key={module.id} className="card">
                <h3>{module.title}</h3>
                <p className="text-sm text-secondary">{module.description}</p>
                <div className="text-xs text-secondary" style={{ marginTop: '0.5rem' }}>
                  Duration: {module.duration_hours} hours
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-secondary">No modules added yet.</p>
        )}
      </div>
    </div>
  )
}

export default TrainingDetail
