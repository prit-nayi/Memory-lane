import api from './api.js'

function accessHeaders(accessCode) {
  return { 'X-Visitor-Access-Code': accessCode }
}

export async function getSlideshowPhotos(accessCode) {
  const response = await api.get('/api/v1/slideshow/photos', {
    headers: accessHeaders(accessCode),
  })
  return response.data.map((photo) => ({
    ...photo,
    image_url: api.getUri({ url: photo.image_url }),
  }))
}

export async function getSlideshowPhotoImage(accessCode, imageUrl) {
  const response = await api.get(imageUrl, {
    headers: accessHeaders(accessCode),
    responseType: 'blob',
  })
  return response.data
}

export async function getSlideshowSettings() {
  const response = await api.get('/api/v1/slideshow/settings')
  return response.data
}
