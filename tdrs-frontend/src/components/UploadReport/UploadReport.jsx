import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import fileInput from '../../assets/uswds/file-input'
import Button from '../Button'
import { history } from '../../configureStore'

import { clearError, upload } from '../../actions/reports'
import FileUpload from '../FileUpload'

function UploadReport() {
  const files = useSelector((state) => state.reports.files)
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

  useEffect(() => {
    fileInput.init()
  }, [])

  return (
    <form>
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
        <Button
          className="cancel"
          type="button"
          onClick={() => history.push('/reports')}
        >
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default UploadReport
