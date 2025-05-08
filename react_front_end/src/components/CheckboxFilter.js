import { useState, useEffect } from "react"

function CheckboxFilter({
  checkboxGroupName,
  checkboxData,
  checkedState,
  setCheckedState,
  setQueryParams,
  withSearch,
  setIsLoading,
}) {
  const [searchQuery, setSearchQuery] = useState("")
  const [filteredData, setFilteredData] = useState(checkboxData)

  useEffect(() => {
    setFilteredData(checkboxData.filter(({ label }) => label.toLowerCase().includes(searchQuery.toLowerCase())))
  }, [searchQuery, checkboxData])

  const handleCheckboxChange = (position) => {
    const updatedCheckedState = checkedState.map((item, index) => (index === position ? !item : item))

    // Generate an array of the names of all checked checkboxes
    const checkedItems = checkboxData.filter((_, index) => updatedCheckedState[index]).map(({ name }) => name)

    setIsLoading(true)
    setQueryParams(checkedItems)
    setCheckedState(updatedCheckedState)
  }

  return (
    <>
      {withSearch ? (
        <SearchCheckboxes
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          checkboxGroupName={checkboxGroupName}
        />
      ) : null}
      <ul
        className={`govuk-list govuk-checkboxes govuk-checkboxes--small fbr-checkbox-filters ${withSearch ? "fbr-max-height-350 fbr-scrollbars-visible" : ""}`}
        data-module="govuk-checkboxes"
        id={`${withSearch ? `${checkboxGroupName}-autocomplete-list` : `${checkboxGroupName}-list`}`}
      >
        {filteredData.map(({ name, label }, index) => (
          <li className="govuk-checkboxes__item" key={name}>
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
    </>
  )
}

function SearchCheckboxes({ searchQuery, setSearchQuery, checkboxGroupName }) {
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value)
  }

  return (
    <div className="govuk-form-group search-group">
      <label className="govuk-label govuk-visually-hidden" htmlFor={`${checkboxGroupName}-autocomplete`}>
        Published by - search {checkboxGroupName}
      </label>
      <div className="search-input-button search-input-button--black fbr-publisher-search">
        <input
          className="govuk-input fbr-publisher-search__input app-site-search__input--default"
          id={`${checkboxGroupName}-autocomplete`}
          name={`${checkboxGroupName}-autocomplete`}
          type="search"
          placeholder="Search"
          value={searchQuery}
          onChange={handleSearchChange}
          role="combobox"
          aria-autocomplete="list"
          aria-controls={`${checkboxGroupName}-autocomplete-list`}
          aria-expanded="true"
          aria-label={`Published by - search ${checkboxGroupName}`}
        />
      </div>
    </div>
  )
}

export { CheckboxFilter }
