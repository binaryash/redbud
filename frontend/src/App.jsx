import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import PrivateRoute from './components/PrivateRoute.jsx'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Trainings from './pages/Trainings.jsx'
import TrainingDetail from './pages/TrainingDetail.jsx'
import Modules from './pages/Modules.jsx'
import Content from './pages/Content.jsx'
import Users from './pages/Users.jsx'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="trainings" element={<Trainings />} />
            <Route path="trainings/:id" element={<TrainingDetail />} />
            <Route path="modules" element={<Modules />} />
            <Route path="content" element={<Content />} />
            <Route path="users" element={<Users />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
