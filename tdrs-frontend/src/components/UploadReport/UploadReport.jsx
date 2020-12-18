import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import fileInput from '../../assets/uswds/file-input'
import Button from '../Button'

import { clearError, upload } from '../../actions/reports'
import FileUpload from '../FileUpload'

function UploadReport() {
  const files = useSelector((state) => state.reports.files)
  const getFile = (fileName) => {
    return files.find((file) => fileName === file.name)
  }
  const dispatch = useDispatch()
  const uploadFiles = ({ target }) => {
    dispatch(clearError({ name: target.name }))
    dispatch(upload({ file: target.files[0], name: target.name }))
      .then((resp) => resp)
      .then((success) => {
        if (!success) {
          const inputTarget = target.parentNode
          const previewHeading = inputTarget.querySelector(
            '.usa-file-input__preview-heading'
          )
          const preview = inputTarget.querySelector('.usa-file-input__preview')
          const instructions = inputTarget.querySelector(
            '.usa-file-input__instructions'
          )
          inputTarget.removeChild(previewHeading)
          inputTarget.removeChild(preview)
          instructions.classList.remove('display-none')
        }
      })
  }

  useEffect(() => {
    fileInput.init()
  }, [])

  return (
    <form>
      <FileUpload file={getFile('activeData')} onUpload={uploadFiles} />
      <FileUpload file={getFile('closedData')} onUpload={uploadFiles} />
      <FileUpload file={getFile('aggregataData')} onUpload={uploadFiles} />
      <FileUpload file={getFile('stratumData')} onUpload={uploadFiles} />
      <div className="buttonContainer margin-y-4">
        <Button type="submit">Submit Files</Button>
        <Button type="button">Cancel</Button>
      </div>
    </form>
  )
}

export default UploadReport
