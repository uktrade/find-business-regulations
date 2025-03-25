function ResultsCount({ isLoading, start, end, totalResults, searchQuery }) {
  return (
    <p className="govuk-body govuk-!-margin-bottom-0" aria-live="polite">
      {isLoading ? (
        "Loading..."
      ) : totalResults ? (
        <>
          {`${start} to ${end} of ${totalResults} results`}
          {searchQuery && (
            <>
              {" matching "}
              <span className="govuk-!-font-weight-bold">{searchQuery}</span>
            </>
          )}
        </>
      ) : (
        "No results found"
      )}
    </p>
  )
}

export { ResultsCount }
