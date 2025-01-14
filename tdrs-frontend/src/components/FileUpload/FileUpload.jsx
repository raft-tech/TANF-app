import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import fileTypeChecker from 'file-type-checker'
import languageEncoding from 'detect-file-encoding-and-language'

import {
  clearError,
  clearFile,
  SET_FILE_ERROR,
  FILE_EXT_ERROR,
  upload,
  download,
} from '../../actions/reports'
import Button from '../Button'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import { handlePreview, getTargetClassName } from './utils'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

const INVALID_EXT_ERROR =
  'Invalid extension. Accepted file types are: .txt, .ms##, .ts##, or .ts###.'

const getEncodedFile = async function (fileBytes, file) {
  // Create a small view of the file to determine the encoding.
  // Saves a lot of time when a user uploads a large file.
  const btyesView = new Uint8Array(fileBytes.slice(0, 500))
  const blobView = new Blob([btyesView], { type: 'text/plain' })
  try {
    const fileInfo = await languageEncoding(blobView)
    const bom = btyesView.slice(0, 3)
    const hasBom = bom[0] === 0xef && bom[1] === 0xbb && bom[2] === 0xbf
    if ((fileInfo && fileInfo.encoding !== 'UTF-8') || hasBom) {
      const utf8Encoder = new TextEncoder()
      const decoder = new TextDecoder(fileInfo.encoding)
      const decodedString = decoder.decode(
        hasBom ? fileBytes.slice(3) : fileBytes
      )
      const utf8Bytes = utf8Encoder.encode(decodedString)
      return new File([utf8Bytes], file.name, file.options)
    }
    return file
  } catch (error) {
    // This also allows the unit tests to work in the same way they did before this change and is a last ditch fallback
    // to ensure consistenct functionality. Because the unit tests expect a Buffer object, but the browser expects a
    // Blob/File. Thus, when the tests run the call to `languageEncoding` raises an exception, and we return the file
    // as is which is then dispatched as it would have been before this change.
    return file
  }
}

function FileUpload({ section, setLocalAlertState }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.submittedFiles)

  const dispatch = useDispatch()

  // e.g. "1 - Active Case Data" => ["1", "Active Case Data"]
  const [sectionNumber, sectionName] = section.split(' - ')

  const hasFile = files?.some(
    (file) => file.section.includes(sectionName) && file.uuid
  )

  const hasPreview = files?.some(
    (file) => file.section.includes(sectionName) && file.name
  )

  const selectedFile = files?.find((file) => file.section.includes(sectionName))

  const formattedSectionName = selectedFile?.section
    .split(' ')
    .map((word) => word.toLowerCase())
    .join('-')

  const targetClassName = getTargetClassName(formattedSectionName)

  const fileName = selectedFile?.fileName || 'report.txt'
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${selectedFile?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  useEffect(() => {
    const trySettingPreview = () => {
      const previewState = handlePreview(fileName, targetClassName)
      if (!previewState) {
        setTimeout(trySettingPreview, 100)
      }
    }
    if (hasPreview || hasFile) {
      trySettingPreview()
    }
  }, [hasPreview, hasFile, fileName, targetClassName])

  const downloadFile = ({ target }) => {
    dispatch(clearError({ section: sectionName }))
    dispatch(download(selectedFile))
  }
  const inputRef = useRef(null)

  const validateAndUploadFile = async (event) => {
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    const { name: section } = event.target
    const file = event.target.files[0]

    // Clear existing errors and the current
    // file in the state if the user is re-uploading
    dispatch(clearError({ section }))
    dispatch(clearFile({ section }))

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const filereader = new FileReader()
    const types = ['png', 'gif', 'jpeg']
    filereader.onload = async (e) => {
      const re = /(\.txt|\.ms\d{2}|\.ts\d{2,3})$/i
      if (!re.exec(file.name)) {
        dispatch({
          type: FILE_EXT_ERROR,
          payload: {
            error: { message: INVALID_EXT_ERROR },
            section,
          },
        })
        return
      }

      const isImg = fileTypeChecker.validateFileType(filereader.result, types)

      if (isImg) {
        createFileInputErrorState(input, dropTarget)

        dispatch({
          type: SET_FILE_ERROR,
          payload: {
            error: { message: INVALID_FILE_ERROR },
            section,
          },
        })
        return
      }

      // Get the correctly encoded file
      const fileToUpload = await getEncodedFile(e.target.result, file)
      dispatch(upload({ file: fileToUpload, section }))
    }

    filereader.readAsArrayBuffer(file)
  }

  return (
    <div
      className={`usa-form-group ${
        selectedFile?.error ? 'usa-form-group--error' : ''
      }`}
    >
      <label className="usa-label text-bold" htmlFor={formattedSectionName}>
        Section {sectionNumber} - {sectionName}
      </label>
      <div>
        {selectedFile?.error && (
          <div
            className="usa-error-message"
            id={`${formattedSectionName}-error-alert`}
            role="alert"
          >
            {selectedFile.error.message}
          </div>
        )}
      </div>
      <div
        id={`${formattedSectionName}-file`}
        aria-hidden
        className="display-none"
      >
        {ariaDescription}
      </div>
      <input
        ref={inputRef}
        onChange={validateAndUploadFile}
        id={formattedSectionName}
        className="usa-file-input"
        type="file"
        name={sectionName}
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage={INVALID_FILE_ERROR}
      />
      <div style={{ marginTop: '25px' }}>
        {hasFile && selectedFile?.id ? (
          <Button
            className="tanf-file-download-btn"
            type="button"
            onClick={downloadFile}
          >
            Download Section {sectionNumber}
          </Button>
        ) : null}
      </div>
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
  setLocalAlertState: PropTypes.func.isRequired,
}

export default FileUpload
