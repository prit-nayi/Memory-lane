import api from './api.js'

export async function getSlideshowPhotos() {
  const response = await api.get('/api/v1/slideshow/photos')
  return response.data.map((photo) => ({
    ...photo,
    image_url: api.getUri({ url: photo.image_url }),
  }))
}

export async function getSlideshowSettings() {
  const response = await api.get('/api/v1/slideshow/settings')
  return response.data
}
