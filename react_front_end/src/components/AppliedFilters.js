import { DOCUMENT_TYPES } from "../utils/constants"

function AppliedFilters({ documentTypeCheckedState, publisherCheckedState, removeFilter, publishers }) {
  // Combine checked document types and publishers into a single array
  const checkedFilters = [
    ...documentTypeCheckedState
      .map((item, index) => (item ? { type: "docType", ...DOCUMENT_TYPES[index] } : null))
      .filter((item) => item !== null),
    ...publisherCheckedState
      .map((item, index) => (item ? { type: "publisher", ...publishers[index] } : null))
      .filter((item) => item !== null),
  ]

  return (
    <ul className="fbr-applied-filters-container">
      {checkedFilters.map((filter, index) => (
        <li className="fbr-applied-filter-tag" key={index}>
          <a href="#delete" onClick={() => removeFilter(filter.type, filter.name)}>
            <span className="govuk-visually-hidden">Remove filter:</span>
            <span className="govuk-body-s">{filter.label}</span>
          </a>
        </li>
      ))}
    </ul>
  )
}

export { AppliedFilters }
