import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import fileInput from '../../assets/uswds/file-input'
import Button from '../Button'

import { clearError, upload } from '../../actions/reports'
import FileUpload from '../FileUpload'
import axiosInstance from '../../axios-instance'

function UploadReport() {
  const user = useSelector((state) => state.auth.user)
  const files = useSelector((state) => state.reports.files)
  const year = useSelector((state) => state.reports.year)
  const getFile = (fileName) => {
    return files.find((file) => fileName === file.section)
  }
  const dispatch = useDispatch()
  const uploadFiles = ({ target }) => {
    dispatch(clearError({ section: target.name }))
    dispatch(
      upload({
        file: target.files[0],
        section: target.name,
      })
    ).then((success) => {
      if (!success) {
        const inputEl = target
        inputEl.value = ''
      }
    })
  }

  const onSubmit = (e) => {
    e.preventDefault()
    const filteredFiles = files.filter((file) => file.fileName)
    filteredFiles.forEach((file) =>
      axiosInstance.post(`${process.env.REACT_APP_BACKEND_URL}/reports/`, {
        original_filename: file.fileName,
        slug: 'hdslajhfdaksdjflajlsdfa',
        user: user.id,
        stt: user.stt.id,
        year,
        quarter: 'Q1',
        section: file.section,
      })
    )
  }

  useEffect(() => {
    fileInput.init()
  }, [])

  return (
    <form onSubmit={onSubmit}>
      <FileUpload
        file={getFile('Active Case Data')}
        section="1"
        onUpload={uploadFiles}
      />
      <FileUpload
        file={getFile('Closed Case Data')}
        section="2"
        onUpload={uploadFiles}
      />
      <FileUpload
        file={getFile('Aggregate Data')}
        section="3"
        onUpload={uploadFiles}
      />
      <FileUpload
        file={getFile('Stratum Data')}
        section="4"
        onUpload={uploadFiles}
      />
      <div className="buttonContainer margin-y-4">
        <Button type="submit">Submit Files</Button>
        <Button type="button">Cancel</Button>
      </div>
    </form>
  )
}

export default UploadReport
