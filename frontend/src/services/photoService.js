import api from './api.js'

function accessHeaders(accessCode) {
  return { 'X-Visitor-Access-Code': accessCode }
}

export async function getMyPhotos(accessCode) {
  const response = await api.get('/api/v1/photos/my-photos', {
    headers: accessHeaders(accessCode),
  })
  return response.data
}

export async function uploadPhotos(accessCode, files, onProgress) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  const response = await api.post('/api/v1/photos/upload', formData, {
    headers: accessHeaders(accessCode),
    onUploadProgress: (event) => {
      if (event.total) {
        onProgress?.(Math.round((event.loaded * 100) / event.total))
      }
    },
  })
  return response.data
}

export async function deletePhoto(accessCode, photoId) {
  await api.delete(`/api/v1/photos/${photoId}`, {
    headers: accessHeaders(accessCode),
  })
}
