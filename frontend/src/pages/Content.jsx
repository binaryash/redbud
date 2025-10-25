import { useAuth } from '../context/AuthContext.jsx'
import api from '../api/axios.js'

const Content = () => {
  const { user } = useAuth()
  const [contents, setContents] = useState([])
  const [trainings, setTrainings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showSummaryModal, setShowSummaryModal] = useState(false)
  const [summaryData, setSummaryData] = useState({ summary: '', loading: false })
  const [selectedContent, setSelectedContent] = useState(null)
  const [detailedContent, setDetailedContent] = useState(null)
  const [maxLength, setMaxLength] = useState(200)
  const [formData, setFormData] = useState({
    training: '',
    title: '',
    description: '',
    content_type: 'text',
    url: '',
    text_content: '',
    order: 0,
    is_active: true,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [contentsRes, trainingsRes] = await Promise.all([
        api.get('/content/contents/'),
        api.get('/users/trainings/'),
      ])
      const contents = contentsRes.data.results || contentsRes.data
      console.log('Content data from API:', contents)
      setContents(contents)
      setTrainings(trainingsRes.data.results || trainingsRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchContentDetail = async (id) => {
    try {
      const response = await api.get(`/content/contents/${id}/`)
      console.log('Detailed content:', response.data)
      return response.data
    } catch (error) {
      console.error('Error fetching content detail:', error)
      return null
    }
  }

  const handleViewDetails = async (content) => {
    const detailed = await fetchContentDetail(content.id)
    if (detailed) {
      setDetailedContent(detailed)
      setShowDetailModal(true)
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
      await api.post('/content/contents/', formData)
      setShowModal(false)
      fetchData()
      setFormData({
        training: '',
        title: '',
        description: '',
        content_type: 'text',
        url: '',
        text_content: '',
        order: 0,
        is_active: true,
      })
    } catch (error) {
      console.error('Error creating content:', error)
      alert('Error creating content')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this content?')) {
      try {
        await api.delete(`/content/contents/${id}/`)
        fetchData()
      } catch (error) {
        console.error('Error deleting content:', error)
        alert('Error deleting content')
      }
    }
  }

  const handleSummarize = async (content) => {
    // Fetch full content details first
    const detailed = await fetchContentDetail(content.id)
    if (!detailed) {
      alert('Failed to fetch content details')
      return
    }

    setSelectedContent(detailed)
    setShowDetailModal(false)
    setShowSummaryModal(true)
    setSummaryData({ summary: '', loading: true })

    try {
      const response = await api.post(`/content/contents/${content.id}/summarize/`, {
        max_length: maxLength,
      })
      setSummaryData({ summary: response.data.summary, loading: false })
    } catch (error) {
      console.error('Error generating summary:', error)
      setSummaryData({
        summary: error.response?.data?.error || error.response?.data?.detail || 'Failed to generate summary',
        loading: false
      })
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
        <h1>Training Content</h1>
        {(user?.role === 'manager' || user?.role === 'trainer') && (
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            Create Content
          </button>
        )}
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Training</th>
              <th>Type</th>
              <th>Order</th>
              <th>Created By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {contents.map((content) => (
              <tr key={content.id}>
                <td>{content.title}</td>
                <td>{content.training_name}</td>
                <td>
                  <span className="badge badge-info">{content.content_type_display}</span>
                </td>
                <td>{content.order}</td>
                <td>{content.created_by_name || 'Unknown'}</td>
                <td>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleViewDetails(content)}
                      className="btn btn-primary btn-sm"
                      title="View Content Details"
                    >
                      View
                    </button>
                    {(user?.role === 'manager' || user?.role === 'trainer') && (
                      <button
                        onClick={() => handleDelete(content.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {contents.length === 0 && (
          <p className="text-center" style={{ padding: '2rem' }}>No content found.</p>
        )}
      </div>

      {/* Create Content Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create Content</h2>
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
                <label className="form-label">Description</label>
                <textarea
                  name="description"
                  className="form-control"
                  value={formData.description}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Content Type *</label>
                <select
                  name="content_type"
                  className="form-control"
                  value={formData.content_type}
                  onChange={handleChange}
                  required
                >
                  <option value="text">Text Content</option>
                  <option value="youtube">YouTube Link</option>
                  <option value="link">External Link</option>
                  <option value="pdf">PDF Document</option>
                  <option value="video">Video</option>
                </select>
              </div>

              {(formData.content_type === 'youtube' ||
                formData.content_type === 'link') && (
                <div className="form-group">
                  <label className="form-label">URL *</label>
                  <input
                    type="url"
                    name="url"
                    className="form-control"
                    value={formData.url}
                    onChange={handleChange}
                    required
                  />
                </div>
              )}

              {formData.content_type === 'text' && (
                <div className="form-group">
                  <label className="form-label">Text Content *</label>
                  <textarea
                    name="text_content"
                    className="form-control"
                    value={formData.text_content}
                    onChange={handleChange}
                    required
                    rows="5"
                  />
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Order</label>
                <input
                  type="number"
                  name="order"
                  className="form-control"
                  value={formData.order}
                  onChange={handleChange}
                  min="0"
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

      {/* Content Detail Modal */}
      {showDetailModal && detailedContent && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h2 className="modal-title">Content Details</h2>
              <button onClick={() => setShowDetailModal(false)} className="modal-close">
                &times;
              </button>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>{detailedContent.title}</h3>
              <div className="flex gap-1" style={{ marginBottom: '1rem' }}>
                <span className="badge badge-info">{detailedContent.content_type_display}</span>
                {detailedContent.hasOwnProperty('is_active') && (
                  <span className={`badge ${detailedContent.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {detailedContent.is_active ? 'Active' : 'Inactive'}
                  </span>
                )}
              </div>
            </div>

            <div className="card" style={{ backgroundColor: 'var(--bg-color)', padding: '1rem', marginBottom: '1rem' }}>
              <div style={{ marginBottom: '0.75rem' }}>
                <strong className="text-sm text-secondary">Training:</strong>
                <p style={{ margin: '0.25rem 0 0 0' }}>{detailedContent.training_name}</p>
              </div>

              {detailedContent.description && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong className="text-sm text-secondary">Description:</strong>
                  <p style={{ margin: '0.25rem 0 0 0' }}>{detailedContent.description}</p>
                </div>
              )}

              {detailedContent.text_content && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong className="text-sm text-secondary">Text Content:</strong>
                  <p style={{
                    margin: '0.25rem 0 0 0',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    padding: '0.5rem',
                    backgroundColor: 'var(--surface-color)',
                    borderRadius: '0.5rem'
                  }}>
                    {detailedContent.text_content}
                  </p>
                </div>
              )}

              {detailedContent.url && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong className="text-sm text-secondary">URL:</strong>
                  <p style={{ margin: '0.25rem 0 0 0' }}>
                    <a href={detailedContent.url} target="_blank" rel="noopener noreferrer">
                      {detailedContent.url}
                    </a>
                  </p>
                </div>
              )}

              {detailedContent.file_url && (
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong className="text-sm text-secondary">File:</strong>
                  <p style={{ margin: '0.25rem 0 0 0' }}>
                    <a href={detailedContent.file_url} target="_blank" rel="noopener noreferrer">
                      Download File
                    </a>
                  </p>
                </div>
              )}

              <div>
                <strong className="text-sm text-secondary">Created:</strong>
                <p style={{ margin: '0.25rem 0 0 0' }}>
                  {new Date(detailedContent.created_at).toLocaleString()} by {detailedContent.created_by_name || 'Unknown'}
                </p>
              </div>
            </div>

            <div className="flex gap-1">
              {(detailedContent.content_type === 'text' || detailedContent.content_type === 'pdf') && (
                <button
                  onClick={() => handleSummarize(detailedContent)}
                  className="btn btn-secondary"
                  title="Generate AI Summary"
                >
                  Generate Summary
                </button>
              )}
              <button
                onClick={() => setShowDetailModal(false)}
                className="btn btn-outline"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Summary Modal */}
      {showSummaryModal && selectedContent && (
        <div className="modal-overlay" onClick={() => setShowSummaryModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">AI-Powered Content Summary</h2>
              <button onClick={() => setShowSummaryModal(false)} className="modal-close">
                &times;
              </button>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{selectedContent.title}</h3>
              <span className="badge badge-info">{selectedContent.content_type_display}</span>
            </div>

            <div className="form-group">
              <label className="form-label">Summary Length (characters)</label>
              <input
                type="number"
                className="form-control"
                value={maxLength}
                onChange={(e) => setMaxLength(parseInt(e.target.value))}
                min="50"
                max="1000"
              />
              <small className="text-secondary">Range: 50-1000 characters</small>
            </div>

            {summaryData.loading ? (
              <div className="loading">
                <div className="spinner"></div>
                <p style={{ marginTop: '1rem', textAlign: 'center' }}>Generating summary with AI...</p>
              </div>
            ) : (
              <>
                {summaryData.summary && (
                  <div className="card" style={{ backgroundColor: 'var(--bg-color)', padding: '1rem' }}>
                    <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                      Summary:
                    </h4>
                    <p style={{ whiteSpace: 'pre-wrap' }}>{summaryData.summary}</p>
                  </div>
                )}

                <div className="flex gap-1" style={{ marginTop: '1rem' }}>
                  <button
                    onClick={() => handleSummarize(selectedContent)}
                    className="btn btn-primary"
                  >
                    Regenerate Summary
                  </button>
                  <button
                    onClick={() => {
                      setShowSummaryModal(false)
                      setShowDetailModal(true)
                    }}
                    className="btn btn-secondary"
                  >
                    Back to Details
                  </button>
                  <button
                    onClick={() => setShowSummaryModal(false)}
                    className="btn btn-outline"
                  >
                    Close
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Content
