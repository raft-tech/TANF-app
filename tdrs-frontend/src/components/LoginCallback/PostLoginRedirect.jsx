import React, { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import {
  clearLoginDestination,
  getLoginDestination,
} from '../../utils/loginRedirect'

function PostLoginRedirect() {
  const [destination] = useState(getLoginDestination)

  useEffect(() => {
    clearLoginDestination()
  }, [])

  return <Navigate to={destination} replace />
}

export default PostLoginRedirect
