import { useContext } from 'react'
import { VisitorContext } from '../context/visitorContext.js'

export function useVisitor() {
  const context = useContext(VisitorContext)
  if (!context) {
    throw new Error('useVisitor must be used within VisitorProvider')
  }
  return context
}
