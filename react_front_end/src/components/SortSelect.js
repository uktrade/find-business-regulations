function SortSelect({ sortQuery, setSortQuery }) {
  const handleSortChange = (e) => {
    setSortQuery([e.target.value])
  }

  return (
    <div className="govuk-grid-row">
      <div className="govuk-grid-column-full">
        <div className="orp-flex">
          <label className="govuk-label govuk-!-margin-right-3 orp-!-no-text-wrap" htmlFor="sort-select">
            Sort by
          </label>
          <select
            className="govuk-select"
            value={sortQuery[0]}
            onChange={handleSortChange}
            id="sort-select"
            aria-label="Sort by"
          >
            <option value="recent">Recently updated</option>
            <option value="relevance">Relevance</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export { SortSelect }
