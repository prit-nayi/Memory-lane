import api from './api.js'

export async function registerVisitor({ name, consent }) {
  const response = await api.post('/api/v1/visitors/register', { name, consent })
  return response.data
}

export async function verifyVisitor(accessCode) {
  const response = await api.post('/api/v1/visitors/verify', {
    access_code: accessCode,
  })
  return response.data
}

export async function getCurrentVisitor(accessCode) {
  const response = await api.get('/api/v1/visitors/me', {
    headers: { 'X-Visitor-Access-Code': accessCode },
  })
  return response.data
}
