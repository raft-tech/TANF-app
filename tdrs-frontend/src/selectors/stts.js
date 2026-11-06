import { selectUser, accountIsRegionalStaff } from './auth'

export const fileTypeToProgramSlug = (fileType, sttType) => {
  if (fileType === 'ssp-moe') return 'ssp'
  if (fileType !== 'tanf') return null
  if (sttType === 'tribe') return 'tribal'
  if (sttType === 'state' || sttType === 'territory') return 'tanf'
  return null
}

const isRecord = (value) =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
const isId = (value) => Number.isSafeInteger(value) && value > 0
const isName = (value) => typeof value === 'string' && value.trim().length > 0
const isProgram = (value) =>
  isRecord(value) && isId(value.id) && isName(value.slug) && isName(value.name)

/** Returns null for an absent record; malformed or ambiguous metadata throws. */
export const getProgramParticipation = (stt, programSlug) => {
  if (!programSlug || stt?.program_participations === undefined) return null
  if (!Array.isArray(stt.program_participations)) {
    throw new Error('Program participations must be an array.')
  }

  let match = null
  stt.program_participations.forEach((participation) => {
    if (
      !isRecord(participation) ||
      !isId(participation.id) ||
      !isProgram(participation.program)
    ) {
      throw new Error('Invalid program participation metadata.')
    }
    if (participation.program.slug !== programSlug) return
    if (match) {
      throw new Error(`Multiple participations for program ${programSlug}.`)
    }
    match = participation
  })
  return match
}

/**
 * Derives membership only from API assignments, not the presentation catalog.
 * Callers must resolve metadata loading before interpreting an absent record.
 * Malformed assignments throw so consumers can show a configuration error.
 */
export const getAssignedSections = (stt, fileType) => {
  const participation = getProgramParticipation(
    stt,
    fileTypeToProgramSlug(fileType, stt?.type)
  )
  if (!participation) return []
  if (!Array.isArray(participation.sections)) {
    throw new Error('Assigned sections must be an array.')
  }

  const sections = new Map()
  participation.sections.forEach((section) => {
    if (
      !isRecord(section) ||
      !isId(section.id) ||
      !isName(section.name) ||
      !isProgram(section.program)
    ) {
      throw new Error('Invalid assigned section metadata.')
    }
    if (
      section.program.id !== participation.program.id ||
      section.program.slug !== participation.program.slug ||
      section.program.name !== participation.program.name
    ) {
      throw new Error(
        'Assigned section does not match its participation program.'
      )
    }
    const existing = sections.get(section.id)
    if (existing && existing.name !== section.name) {
      throw new Error('Conflicting names for the same assigned section ID.')
    }
    sections.set(section.id, {
      id: section.id,
      name: section.name,
      program: { ...section.program },
    })
  })
  return [...sections.values()]
}

/** Identity comes from the active control/profile, never reports.stt. */
export const resolveReportStt = ({
  user,
  canSelectStt,
  isRegionalStaff,
  catalog,
  selectedName,
}) => {
  const loaded = catalog?.loaded || catalog?.sttList?.length > 0
  if (!user) return { state: 'loading', stt: null }
  if (isRegionalStaff) {
    if (!Array.isArray(user.regions)) return { state: 'loading', stt: null }
    const stt = user.regions
      .flatMap((region) => region.stts || [])
      .find((stt) => stt.name === selectedName)
    return { state: 'ready', stt: stt || null }
  }
  if (canSelectStt) {
    if (!loaded)
      return { state: catalog?.error ? 'error' : 'loading', stt: null }
    return {
      state: 'ready',
      stt: catalog.sttList.find((stt) => stt.name === selectedName) || null,
    }
  }
  const profile = user.stt
  if (!profile?.id) return { state: 'ready', stt: null }
  if (selectedName && selectedName !== profile.name)
    return { state: 'ready', stt: null, unauthorized: true }
  // A completed catalog (including []) is authoritative, not a truthiness
  // check on sections. Profile metadata is usable before catalog arrival.
  if (loaded)
    return {
      state: 'ready',
      stt: catalog.sttList.find((stt) => stt.id === profile.id) || null,
    }
  if (catalog?.loading) return { state: 'loading', stt: null }
  if (Object.hasOwn(profile, 'program_participations'))
    return { state: 'ready', stt: profile, provisional: true }
  return { state: catalog?.error ? 'error' : 'loading', stt: null }
}

export const availableStts = (path) => {
  return (state) => {
    const filterTribes = (stts = []) => {
      if (path.includes('fra')) {
        return stts.filter((stt) => stt.type !== 'tribe')
      }
      return stts
    }

    if (accountIsRegionalStaff(state)) {
      const regionalStts =
        selectUser(state)
          .regions?.map((region) => region.stts)
          .flat() || []
      return filterTribes(regionalStts).sort((a, b) =>
        a.name.localeCompare(b.name)
      )
    }

    return filterTribes(state?.stts?.sttList || [])
  }
}
