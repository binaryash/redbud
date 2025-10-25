import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav style={{
      backgroundColor: 'var(--surface-color)',
      boxShadow: 'var(--shadow)',
      padding: '1rem 0',
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <Link to="/" style={{
            fontSize: '1.25rem',
            fontWeight: '600',
            textDecoration: 'none',
            color: 'var(--primary-color)',
          }}>
            Training System
          </Link>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/dashboard" style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
              Dashboard
            </Link>
            <Link to="/trainings" style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
              Trainings
            </Link>
            <Link to="/modules" style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
              Modules
            </Link>
            <Link to="/content" style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
              Content
            </Link>
            {user?.role === 'manager' && (
              <Link to="/users" style={{ textDecoration: 'none', color: 'var(--text-color)' }}>
                Users
              </Link>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {user?.email} ({user?.role})
          </span>
          <button onClick={handleLogout} className="btn btn-outline">
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
