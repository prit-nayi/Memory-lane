import api from './api.js'

function adminHeaders(token) {
  return { Authorization: `Bearer ${token}` }
}

export async function loginAdmin(username, password) {
  const response = await api.post('/api/v1/admin/login', { username, password })
  return response.data
}

export async function getAdminDashboard(token) {
  const response = await api.get('/api/v1/admin/dashboard', {
    headers: adminHeaders(token),
  })
  return response.data
}

export async function getAdminVisitors(token) {
  const response = await api.get('/api/v1/admin/visitors', {
    headers: adminHeaders(token),
  })
  return response.data
}

export async function updateAdminVisitor(token, visitorId, isActive) {
  const response = await api.patch(
    `/api/v1/admin/visitors/${visitorId}`,
    { is_active: isActive },
    { headers: adminHeaders(token) },
  )
  return response.data
}

export async function getAdminPhotos(token, visitorId) {
  const response = await api.get('/api/v1/admin/photos', {
    headers: adminHeaders(token),
    params: visitorId ? { visitor_id: visitorId } : undefined,
  })
  return response.data
}

export async function deleteAdminPhoto(token, photoId) {
  await api.delete(`/api/v1/admin/photos/${photoId}`, {
    headers: adminHeaders(token),
  })
}

export async function getAdminSettings(token) {
  const response = await api.get('/api/v1/admin/settings', {
    headers: adminHeaders(token),
  })
  return response.data
}

export async function updateAdminSettings(token, settings) {
  const response = await api.put('/api/v1/admin/settings', settings, {
    headers: adminHeaders(token),
  })
  return response.data
}
