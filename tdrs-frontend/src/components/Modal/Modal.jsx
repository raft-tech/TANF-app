import React from 'react'
import Button from '../Button'

const Modal = ({ title, message, buttons = [], isVisible = false }) =>
  isVisible ? (
    <div id="modal" className="modal display-block">
      <div className="modal-content">
        <h1
          className="font-serif-xl margin-4 margin-bottom-0 text-normal"
          tabIndex="-1"
        >
          {title}
        </h1>
        <p className="margin-4 margin-top-1">{message}</p>
        <div className="margin-x-4 margin-bottom-4">
          {buttons.map((b) => (
            <Button
              key={b.key}
              type="button"
              className="mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
              onClick={b.onClick}
            >
              {b.text}
            </Button>
          ))}
        </div>
      </div>
    </div>
  ) : null

export default Modal
