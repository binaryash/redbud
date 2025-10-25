import React from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'

const Layout = () => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, padding: '2rem 0' }}>
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
