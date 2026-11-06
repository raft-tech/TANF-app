import { programSlugToResponseCode } from '../../utils/reportSections'
import { CaseAggregatesTable } from './components/CaseAggregatesTable'
import { TotalAggregatesTable } from './components/TotalAggregatesTable'
import { PaginatedHistory } from './components/PaginatedHistory'
import KnowledgeCenterLink from './components/KnowledgeCenterLink'
import { useSubmissionHistory } from '../../hooks/useSubmissionHistory'

const SectionSubmissionHistory = ({
  filterValues,
  reprocessedState,
  sections = [],
  program,
}) => {
  const { files, loading } = useSubmissionHistory(filterValues, {
    scoped: true,
    enabled: sections.length > 0 && Boolean(program),
  })

  return (
    <>
      <KnowledgeCenterLink />
      <div>
        {sections.map((section) => {
          const sectionNumber = section.number
          const TableComponent =
            section.tableKind === 'case'
              ? CaseAggregatesTable
              : TotalAggregatesTable

          return (
            <PaginatedHistory
              key={section.id}
              caption={`Section ${sectionNumber} - ${section.name}`}
              files={files.filter(
                (f) =>
                  f.section === section.name &&
                  f.program_type === programSlugToResponseCode(program.slug)
              )}
              loading={loading}
              reprocessedState={reprocessedState}
              TableComponent={TableComponent}
            />
          )
        })}
      </div>
    </>
  )
}

export default SectionSubmissionHistory
