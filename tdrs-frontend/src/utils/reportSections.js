import {
  fileTypeToProgramSlug,
  getProgramParticipation,
  getAssignedSections,
} from '../selectors/stts'
import {
  getUploadAssignmentKey,
  sameSection,
  sameUploadScope,
} from './reportScopes'

const SECTION_PRESENTATION = {
  'Active Case Data': { number: 1, tableKind: 'case' },
  'Closed Case Data': { number: 2, tableKind: 'case' },
  'Aggregate Data': { number: 3, tableKind: 'total' },
  'Stratum Data': { number: 4, tableKind: 'total' },
}

const RESPONSE_PROGRAM_CODES = {
  tanf: 'TAN',
  tribal: 'TRIBAL',
  ssp: 'SSP',
}

export const programSlugToResponseCode = (slug) =>
  Object.hasOwn(RESPONSE_PROGRAM_CODES, slug)
    ? RESPONSE_PROGRAM_CODES[slug]
    : null

/** Adds presentation metadata without granting sections or changing API names. */
export const presentReportSections = (sections) => {
  if (!Array.isArray(sections)) {
    throw new Error('Assigned sections must be an array.')
  }
  return sections
    .map((section) => {
      if (!section || !Object.hasOwn(SECTION_PRESENTATION, section.name)) {
        throw new Error(`Unsupported report section: ${section?.name}.`)
      }
      return { ...section, ...SECTION_PRESENTATION[section.name] }
    })
    .sort((a, b) => a.number - b.number)
}

export const getTdrAssignment = (sttResolution, fileType, piaEnabled = false) => {
  const { stt, state: metadataState } = sttResolution
  const piaOption = {
    label: 'Program Integrity Audit',
    value: 'program-integrity-audit',
  }
  const sspOption = { label: 'SSP-MOE', value: 'ssp-moe' }
  const piaOptions = []

  if (piaEnabled && stt && stt.type !== 'tribe') {
    piaOptions.push(piaOption)
  }

  const emptyAssignment = {
    sections: [],
    program: null,
    options: piaOptions,
    state: metadataState,
  }

  if (metadataState !== 'ready' || !stt) return emptyAssignment

  try {
    const tanfProgramSlug = fileTypeToProgramSlug('tanf', stt.type)
    const tanfParticipation = getProgramParticipation(stt, tanfProgramSlug)
    const sspParticipation = getProgramParticipation(stt, 'ssp')
    const options = []

    if (tanfParticipation) {
      const tanfOption = { label: tanfParticipation.program.name, value: 'tanf' }
      options.push(tanfOption)
    }

    if (sspParticipation) {
      getAssignedSections(stt, 'ssp-moe')
      options.push(sspOption)
    }

    options.push(...piaOptions)

    const selectedProgramSlug = fileTypeToProgramSlug(fileType, stt.type)
    const selectedParticipation = getProgramParticipation(
      stt,
      selectedProgramSlug
    )
    const isSelectedOptionAvailable = options.some(
      ({ value }) => value === fileType
    )
    let program = null
    let sections = []

    if (isSelectedOptionAvailable) {
      program = selectedParticipation?.program || null
      sections = presentReportSections(getAssignedSections(stt, fileType))
    }

    return {
      state: 'ready',
      options,
      program,
      sections,
    }
  } catch (error) {
    return { ...emptyAssignment, state: 'error', error: error.message }
  }
}

/** Reject the whole batch, including staged slots that are not visible inputs. */
export const validateTdrSubmission = ({
  stt,
  program,
  sections,
  uploadScope,
  reports,
  year,
  quarter,
}) => {
  if (
    !stt?.id ||
    !program ||
    !sections.length ||
    !sameUploadScope(reports.uploadScope, uploadScope) ||
    String(uploadScope.sttId) !== String(stt.id) ||
    uploadScope.key !==
      getUploadAssignmentKey({ sttId: stt.id, program, sections }) ||
    uploadScope.program.id !== program.id ||
    uploadScope.program.slug !== program.slug
  )
    return 'Report assignments changed. Select an assigned program and reload your files before submitting.'
  const staged = reports.submittedFiles.filter(
    (file) => file.fileName && !file.id
  )
  if (
    staged.some(
      (file) =>
        !file.uuid || !sections.some((section) => sameSection(file, section))
    )
  )
    return 'A staged file is no longer assigned to this STT and program. Clear and reload your files before submitting.'
  if (!year || !quarter)
    return 'Select a fiscal year and quarter before submitting.'
  return null
}
