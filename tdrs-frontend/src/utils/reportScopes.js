export const sameUploadScope = (left, right) =>
  Boolean(
    left &&
    right &&
    left.key === right.key &&
    left.generation === right.generation
  )

export const sameSection = (file, descriptor) =>
  file.section === descriptor.name &&
  file.sectionId === descriptor.id &&
  file.program?.id === descriptor.program?.id &&
  file.program?.slug === descriptor.program?.slug

// Fiscal corrections revalidate staged files; they do not change membership.
export const getUploadAssignmentKey = ({ sttId, program, sections }) =>
  JSON.stringify([
    String(sttId),
    program.id,
    program.slug,
    sections
      .map(({ id, name, program }) => [id, name, program.id, program.slug])
      .sort((a, b) => a[0] - b[0]),
  ])

export const getHistoryQueryKey = ({ stt, file_type, year, quarter = 'Q1' }) =>
  stt?.id && file_type && year
    ? JSON.stringify([String(stt.id), file_type, String(year), quarter || null])
    : null

export const sameHistoryScope = (left, right) =>
  Boolean(
    left &&
    right &&
    left.key === right.key &&
    left.requestId === right.requestId
  )

export const isUploadCurrent = (reports, uploadScope, files = []) =>
  sameUploadScope(reports.uploadScope, uploadScope) &&
  files.every((file) =>
    reports.submittedFiles.some(
      (slot) =>
        sameSection(slot, {
          id: file.sectionId,
          name: file.section,
          program: file.program,
        }) && slot.uuid === file.uuid
    )
  )
