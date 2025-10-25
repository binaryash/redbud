import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import api from '../api/axios.js'

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    trainings: 0,
    modules: 0,
    content: 0,
    users: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [trainings, modules, content, users] = await Promise.all([
        api.get('/users/trainings/'),
        api.get('/users/modules/'),
        api.get('/content/contents/'),
        user?.role === 'manager' ? api.get('/users/users/') : Promise.resolve({ data: { count: 0 } }),
      ])

      setStats({
        trainings: trainings.data.count || trainings.data.results?.length || 0,
        modules: modules.data.count || modules.data.results?.length || 0,
        content: content.data.count || content.data.results?.length || 0,
        users: users.data.count || users.data.results?.length || 0,
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
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

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>
        Welcome, {user?.first_name || user?.username}!
      </h1>

      <div className="grid grid-3">
        <div className="card">
          <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
            Total Trainings
          </h3>
          <p style={{ fontSize: '2rem', fontWeight: '600', color: 'var(--primary-color)' }}>
            {stats.trainings}
          </p>
        </div>

        <div className="card">
          <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
            Training Modules
          </h3>
          <p style={{ fontSize: '2rem', fontWeight: '600', color: 'var(--success-color)' }}>
            {stats.modules}
          </p>
        </div>

        <div className="card">
          <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
            Content Items
          </h3>
          <p style={{ fontSize: '2rem', fontWeight: '600', color: 'var(--warning-color)' }}>
            {stats.content}
          </p>
        </div>

        {user?.role === 'manager' && (
          <div className="card">
            <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              Total Users
            </h3>
            <p style={{ fontSize: '2rem', fontWeight: '600', color: 'var(--secondary-color)' }}>
              {stats.users}
            </p>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>Your Role: {user?.role}</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          {user?.role === 'manager' && 'As a manager, you have full access to all features including user management, training creation, and assignments.'}
          {user?.role === 'trainer' && 'As a trainer, you can manage trainings assigned to you, create modules and content.'}
          {user?.role === 'employee' && 'As an employee, you can view your assigned trainings and access training content.'}
        </p>
      </div>
    </div>
  )
}

export default Dashboard
