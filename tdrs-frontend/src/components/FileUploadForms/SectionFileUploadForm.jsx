import React from 'react'
import Button from '../Button'
import FileUpload from '../FileUpload'
import { useFileUploadForm } from '../../hooks/useFileUploadForm'
import { sameSection } from '../../utils/reportScopes'
import { validateTdrSubmission } from '../../utils/reportSections'

const SectionFileUploadForm = ({
  stt,
  sections = [],
  program,
  programLabel,
  uploadScope,
}) => {
  // No file transformation needed for section uploads
  const transformFiles = null

  // Format sections for success message (1, 2, 3, etc.)
  const formatSections = (uploadedFiles) => {
    const uploadedSections = uploadedFiles
      ? uploadedFiles
          .map(
            (file) =>
              sections.find((section) => sameSection(file, section))?.number
          )
          .join(', ')
          .split(' ')
      : []

    if (uploadedSections.length > 1) {
      uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
    }

    return uploadedSections.join(' ')
  }

  // Generate submit payload for section uploads
  const getSubmitPayload = ({
    quarter,
    year,
    formattedSections,
    logger,
    setUploadAlertState,
    setProcessingAlertState,
    stt,
    uploadedFiles,
    user,
    fileType,
  }) => ({
    quarter,
    year,
    formattedSections,
    logger,
    setUploadAlertState,
    setProcessingAlertState,
    stt,
    uploadedFiles,
    user,
    ssp: fileType === 'ssp-moe',
    fileType,
  })

  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    uploadedFiles,
    isSubmitting,
    onSubmit,
    handleCancel,
    setUploadAlertState,
    setProcessingAlertState,
  } = useFileUploadForm({
    stt,
    transformFiles,
    formatSections,
    getSubmitPayload,
    uploadScope,
    validateSubmission: (values) =>
      validateTdrSubmission({
        ...values,
        stt,
        program,
        sections,
        uploadScope,
      }),
  })

  return (
    <>
      <form onSubmit={onSubmit}>
        <fieldset disabled={isSubmitting || !uploadScope || !sections.length}>
          {sections.map((section) => (
            <FileUpload
              key={`${uploadScope?.generation}:${section.id}`}
              section={section.name}
              sectionDescriptor={section}
              uploadScope={uploadScope}
              label={`Section ${section.number} - ${programLabel} - ${section.name}`}
              year={yearInputValue}
              quarter={quarterInputValue}
              fileType={fileTypeInputValue}
              setUploadAlertState={setUploadAlertState}
              setProcessingAlertState={setProcessingAlertState}
            />
          ))}

          <div className="buttonContainer margin-y-4">
            <Button
              className="card:margin-y-1"
              type="submit"
              disabled={isSubmitting || !uploadScope || !sections.length}
              data-has-uploaded-files={uploadedFiles.length > 0}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Data Files'}
            </Button>

            <Button className="cancel" type="button" onClick={handleCancel}>
              Cancel
            </Button>
          </div>
        </fieldset>
      </form>
    </>
  )
}

export default SectionFileUploadForm
