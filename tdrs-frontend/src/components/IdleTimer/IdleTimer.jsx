import React, { useState, useEffect } from 'react'
import { useIdleTimer } from 'react-idle-timer'
import axios from 'axios'
import Button from '../Button'

function IdleTimer() {
  const [isModalVisible, setIsModalVisible] = useState(false)

  // useEffect(() => {
  //   const keyListener = (e) => {
  //     if (e.keyCode === 27) {
  //       onRenewSession()
  //     }
  //   }

  //   document.addEventListener('keydown', keyListener)

  //   return () => document.removeEventListener('keydown', keyListener)
  // })

  const onSignOut = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  const onRenewSession = () => {
    axios.post('/v1/authorization-check')
  }

  useIdleTimer({
    // timeout: 1000 * 60 * 20,
    timeout: 1000 * 3,
    onIdle: () => setIsModalVisible(true),
  })

  return (
    <div
      id="myModal"
      className={`modal ${isModalVisible ? 'display-block' : 'display-none'}`}
    >
      <div className="modal-content">
        <div className="modal-header">
          <h1 className="font-serif-2xl margin-bottom-0 text-normal">
            Your session is about to expire!
          </h1>
        </div>
        <div className="modal-body">
          <p>
            Your TANF Data Portal session will expire due to inactivity in three
            minutes. Any unsaved data will be lost if you allow the session to
            expire. Click the button below to continue your session.
          </p>
        </div>
        <div className="modal-footer">
          <Button
            type="button"
            className="margin-1 sign-out"
            onClick={onSignOut}
          >
            Sign Out
          </Button>
          <Button
            type="button"
            className="margin-1 renew-session"
            onClick={onRenewSession}
          >
            Stay Signed In
          </Button>
        </div>
      </div>
    </div>
  )
}

export default IdleTimer
