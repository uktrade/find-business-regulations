function DocTypeFilters({
  checkboxGroupName,
  checkboxData,
  checkedState,
  setCheckedState,
  setQueryParams,
  withSearch,
  setIsLoading,
}) {
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
      <ul
        className="govuk-list govuk-checkboxes govuk-checkboxes--small fbr-checkbox-filters"
        data-module="govuk-checkboxes"
        id={`${withSearch ? `${checkboxGroupName}-autocomplete-list` : `${checkboxGroupName}-list`}`}
      >
        {checkboxData.map(({ name, label }, index) => (
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

export { DocTypeFilters }
