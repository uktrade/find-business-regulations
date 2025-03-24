function ResultsCount({ isLoading, start, end, totalResults }) {
  return (
    <p className="govuk-body govuk-!-font-weight-bold govuk-!-margin-bottom-0" aria-live="polite">
      {isLoading ? "Loading..." : totalResults ? `${start} to ${end} of ${totalResults} results` : "No results found"}
    </p>
  )
}

export { ResultsCount }
