import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fetchSttList } from '../../actions/sttList'
import ComboBox from '../ComboBox'
import Button from '../Button'

/**
 * @param {function} selectStt - Function to reference and change the
 * selectedStt state.
 * @param {string} selectedStt - The currently selected stt controlled
 * in state elsewhere.
 * @param {function} handleBlur - Runs on blur of combo box element.
 * @param {function} error - Reference to stt errors object.
 */

function STTComboBox({ selectStt, selectedStt, handleBlur, error }) {
  const sttList = useSelector((state) => state?.stts?.sttList)
  const dispatch = useDispatch()
  const [numTries, setNumTries] = useState(0)
  const [reachedMaxTries, setReachedMaxTries] = useState(false)

  useEffect(() => {
    if (sttList.length === 0 && numTries <= 5) {
      dispatch(fetchSttList())
      setNumTries(numTries + 1)
    } else if (sttList.length === 0 && numTries > 5 && !reachedMaxTries) {
      setReachedMaxTries(true)
    }
  }, [dispatch, sttList, numTries, reachedMaxTries])

  const modalRef = useRef()
  const headerRef = useRef()
  const onSignOut = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  return (
    <>
      <ComboBox
        name="stt"
        label="Associated State, Tribe, or Territory*"
        error={error ? 'A state, tribe, or territory is required' : undefined}
        handleSelect={selectStt}
        selected={selectedStt}
        handleBlur={handleBlur}
        placeholder="- Select or Search -"
        aria-required="true"
      >
        <option value="" disabled hidden>
          - Select or Search -
        </option>
        {sttList.map((stt) => (
          <option className="sttOption" key={stt.id} value={stt.name}>
            {stt.name}
          </option>
        ))}
      </ComboBox>
      <div
        id="emptySttListModal"
        className={`modal ${
          reachedMaxTries ? 'display-block' : 'display-none'
        }`}
      >
        <div className="modal-content" ref={modalRef}>
          <h1
            className="font-serif-xl margin-4 margin-bottom-0 text-normal"
            tabIndex="-1"
            ref={headerRef}
          >
            TDP systems are currently experiencing technical difficulties.
          </h1>
          <p className="margin-4 margin-top-1">
            Please sign out and try signing in again. If the issue persists
            contact support at tanfdata@acf.hhs.gov.
          </p>
          <div className="margin-x-4 margin-bottom-4">
            <Button type="button" className="sign-out" onClick={onSignOut}>
              Sign Out Now
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}

STTComboBox.propTypes = {
  selectStt: PropTypes.func.isRequired,
  handleBlur: PropTypes.func,
  selectedStt: PropTypes.string,
  error: PropTypes.bool,
}

STTComboBox.defaultProps = {
  handleBlur: null,
  selectedStt: '',
  error: null,
}
export default STTComboBox
