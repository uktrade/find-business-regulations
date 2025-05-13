import { useState, useEffect } from "react"

function PublisherFilters({
  checkboxGroupName,
  checkboxData,
  checkedState,
  setCheckedState,
  setQueryParams,
  setIsLoading,
}) {
  const [searchQuery, setSearchQuery] = useState("")
  const [filteredData, setFilteredData] = useState(checkboxData)
  const [highlightedIndex, setHighlightedIndex] = useState(-1) // Tracks the highlighted option

  useEffect(() => {
    setFilteredData(
      checkboxData
        .filter(({ label }) => label.toLowerCase().includes(searchQuery.toLowerCase()))
        .sort((a, b) => a.name.localeCompare(b.name)), // Sort alphabetically by name
    )
  }, [searchQuery, checkboxData])

  const handleCheckboxChange = (position) => {
    const updatedCheckedState = checkedState.map((item, index) => (index === position ? !item : item))

    // Generate an array of the names of all checked checkboxes
    const checkedItems = checkboxData.filter((_, index) => updatedCheckedState[index]).map(({ name }) => name)

    setIsLoading(true)
    setQueryParams(checkedItems)
    setCheckedState(updatedCheckedState)
  }

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value)
    setHighlightedIndex(-1) // Reset highlight when the query changes
  }

  const handleKeyDown = (event) => {
    if (filteredData.length === 0) return

    switch (event.key) {
      case "ArrowDown":
        event.preventDefault()
        setHighlightedIndex((prevIndex) => (prevIndex < filteredData.length - 1 ? prevIndex + 1 : 0))
        break
      case "ArrowUp":
        event.preventDefault()
        setHighlightedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : filteredData.length - 1))
        break
      case "Enter":
        event.preventDefault()
        if (highlightedIndex >= 0) {
          setSearchQuery(filteredData[highlightedIndex].label)
        }
        break
      default:
        break
    }
  }

  return (
    <div className="govuk-form-group search-group">
      <label className="govuk-label govuk-visually-hidden" htmlFor={`${checkboxGroupName}-autocomplete`}>
        Published by - search {checkboxGroupName}
      </label>
      <div className="search-input-button search-input-button--black fbr-publisher-search govuk-!-margin-bottom-4">
        <input
          className="govuk-input fbr-publisher-search__input app-site-search__input--default"
          id={`${checkboxGroupName}-autocomplete`}
          name={`${checkboxGroupName}-autocomplete`}
          type="search"
          placeholder="Search"
          value={searchQuery}
          onChange={handleSearchChange}
          onKeyDown={handleKeyDown}
          role="combobox"
          aria-autocomplete="list"
          aria-controls={`${checkboxGroupName}-autocomplete-list`}
          aria-expanded={filteredData.length > 0}
          aria-activedescendant={highlightedIndex >= 0 ? `${checkboxGroupName}-option-${highlightedIndex}` : undefined}
          aria-label={`Published by - search ${checkboxGroupName}`}
        />
      </div>
      {filteredData.length > 0 && (
        <ul
          className="govuk-list govuk-checkboxes govuk-checkboxes--small fbr-checkbox-filters fbr-max-height-350 fbr-scrollbars-visible"
          id={`${checkboxGroupName}-autocomplete-list`}
          role="listbox"
        >
          {filteredData.map(({ label, name }, index) => (
            <li
              key={name}
              id={`${checkboxGroupName}-option-${index}`}
              role="option"
              aria-selected={highlightedIndex === index}
              className={`govuk-checkboxes__item ${highlightedIndex === index ? "highlighted" : ""}`}
            >
              <input
                className="govuk-checkboxes__input"
                type="checkbox"
                id={`checkbox-${name}`}
                name={name}
                value={name}
                checked={checkedState[index]}
                onChange={() => handleCheckboxChange(index)}
                aria-labelledby={`label-${name}`}
              />
              <label className="govuk-label govuk-checkboxes__label" htmlFor={`checkbox-${name}`} id={`label-${name}`}>
                {label}
              </label>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export { PublisherFilters }
