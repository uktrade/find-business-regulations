import { useState, useEffect, useMemo, useCallback } from "react"
import { useQueryParams } from "./hooks/useQueryParams"
import { fetchData } from "./utils/fetch-drf"
import { DOCUMENT_TYPES, PUBLISHERS_URL } from "./utils/constants"

import { Search } from "./components/Search"
import { CheckboxFilter } from "./components/CheckboxFilter"
import { AppliedFilters } from "./components/AppliedFilters"
import { Results } from "./components/Results"
import { Pagination } from "./components/Pagination"
import { ResultsCount } from "./components/ResultsCount"
import { SortSelect } from "./components/SortSelect"
import { NoResultsContent } from "./components/NoResultsContent"

const generateCheckedState = (checkboxes, queryValues) => {
  return checkboxes.map(({ name }) => queryValues.includes(name))
}

function App() {
  const [searchQuery, setSearchQuery] = useQueryParams("search", [])
  const [docTypeQuery, setDocTypeQuery] = useQueryParams("document_type", [])
  const [publisherQuery, setPublisherQuery] = useQueryParams("publisher", [])
  const [sortQuery, setSortQuery] = useQueryParams("sort", ["recent"])
  const [pageQuery, setPageQuery] = useQueryParams("page", [1])

  const [searchInput, setSearchInput] = useState(searchQuery[0] || "") // Set initial state to query parameter value
  const [data, setData] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSearchSubmitted, setIsSearchSubmitted] = useState(false)
  const [publishers, setPublishers] = useState([]) // Add publishers state
  const [publisherCheckedState, setPublisherCheckedState] = useState([])
  const [pageTitle, setPageTitle] = useState("Find business regulations")

  useEffect(() => {
    const fetchPublishers = async () => {
      try {
        const response = await fetch(PUBLISHERS_URL)
        if (!response.ok) {
          throw new Error("Network response was not ok")
        }
        const data = await response.json()
        setPublishers(data.results)
        setPublisherCheckedState(generateCheckedState(data.results, publisherQuery))
      } catch (error) {
        console.error("There was a problem with fetching the publishers:", error)
      }
    }

    fetchPublishers()
  }, [])

  // Memoize the initial checked state for document types and publishers
  const initialDocumentTypeCheckedState = useMemo(
    () => generateCheckedState(DOCUMENT_TYPES, docTypeQuery),
    [docTypeQuery],
  )
  const [documentTypeCheckedState, setDocumentTypeCheckedState] = useState(initialDocumentTypeCheckedState)

  // Memoize the handleSearchChange function
  const handleSearchChange = useCallback(
    (event) => {
      setSearchInput(event.target.value)
    },
    [setSearchInput],
  )

  const handleDeleteFilter = (filterName, filter) => {
    const updateQueryAndState = (query, setQuery, setCheckedState, data) => {
      const updatedQuery = query.filter((item) => item !== filter)
      setQuery(updatedQuery)
      setCheckedState(generateCheckedState(data, updatedQuery))
    }

    if (filterName === "docType") {
      updateQueryAndState(docTypeQuery, setDocTypeQuery, setDocumentTypeCheckedState, DOCUMENT_TYPES)
    } else if (filterName === "publisher") {
      updateQueryAndState(publisherQuery, setPublisherQuery, setPublisherCheckedState, publishers)
    }
  }

  const handleClearFilters = (event) => {
    event.preventDefault()
    setDocTypeQuery([])
    setPublisherQuery([])
    setDocumentTypeCheckedState(generateCheckedState(DOCUMENT_TYPES, []))
    setPublisherCheckedState(generateCheckedState(publishers, []))
  }

  const fetchDataWithLoading = async (queryString) => {
    setIsLoading(true)
    try {
      const data = await fetchData(queryString)
      setData(data)
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchSubmit = useCallback(() => {
    setIsSearchSubmitted(true)
    setSearchQuery([searchInput])
    setPageQuery([1]) // Set the page to 1 when a new search is made

    const filterParams = {
      ...(searchInput.length > 0 && { search: searchInput }),
      ...(docTypeQuery.length > 0 && { document_type: docTypeQuery }),
      ...(publisherQuery.length > 0 && { publisher: publisherQuery }),
      sort: sortQuery.join(","),
      page: [1], // Set page to 1 for new search
    }

    fetchDataWithLoading(filterParams)
  }, [searchInput, docTypeQuery, publisherQuery, sortQuery, setPageQuery])

  useEffect(() => {
    if (isSearchSubmitted) {
      setIsSearchSubmitted(false)
      return
    }

    const handler = setTimeout(() => {
      const filterParams = {
        ...(searchQuery.length > 0 && { search: searchQuery.join(",") }),
        ...(docTypeQuery.length > 0 && { document_type: docTypeQuery }),
        ...(publisherQuery.length > 0 && { publisher: publisherQuery }),
        sort: sortQuery.join(","),
        page: pageQuery.map(Number),
      }

      fetchDataWithLoading(filterParams)
    }, 300) // Adjust the delay as needed

    return () => {
      clearTimeout(handler)
    }
  }, [searchQuery, docTypeQuery, publisherQuery, sortQuery, pageQuery])

  useEffect(() => {
    if (searchQuery.length > 0) {
      const newTitle = `${searchQuery.join(", ")} - page ${pageQuery[0]} - Find business regulations`
      setPageTitle(newTitle)
    } else {
      setPageTitle("Find business regulations")
    }
  }, [searchQuery, pageQuery])

  useEffect(() => {
    document.title = pageTitle
  }, [pageTitle])

  return (
    <div className="govuk-grid-row search-form">
      <div className="govuk-grid-column-one-third">
        <Search
          handleSearchChange={handleSearchChange}
          searchInput={searchInput}
          handleSearchSubmit={handleSearchSubmit}
        />
        <div className="govuk-form-group ">
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--m">
              <h2 className="govuk-fieldset__heading">Document type</h2>
            </legend>
            <CheckboxFilter
              checkboxData={DOCUMENT_TYPES}
              checkedState={documentTypeCheckedState}
              setCheckedState={setDocumentTypeCheckedState}
              setQueryParams={setDocTypeQuery}
              withSearch={false}
              setIsLoading={setIsLoading}
            />
          </fieldset>
        </div>
        <div className="govuk-form-group">
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--m">
              <h2 className="govuk-fieldset__heading">Published by</h2>
            </legend>
            {publishers ? (
              <CheckboxFilter
                checkboxData={publishers}
                checkedState={publisherCheckedState}
                setCheckedState={setPublisherCheckedState}
                setQueryParams={setPublisherQuery}
                withSearch={true}
                setIsLoading={setIsLoading}
              />
            ) : (
              <p className="govuk-body">Loading publishers...</p>
            )}
          </fieldset>
        </div>
        <hr className="govuk-section-break govuk-section-break--m govuk-section-break--visible" />
        <p className="govuk-body">
          <a
            id="download-csv-link"
            href={`download_csv/?${new URLSearchParams({
              search: searchQuery.join(","),
              document_type: docTypeQuery.join(","),
              publisher: publisherQuery.join(","),
              sort: sortQuery.join(","),
              page: pageQuery.join(","),
            }).toString()}`}
            className="govuk-link govuk-link--no-visited-state govuk-!-float-right"
          >
            Download search results as CSV file
          </a>
        </p>
      </div>
      <div className="govuk-grid-column-two-thirds">
        <div className="fbr-flex fbr-flex--space-between">
          <ResultsCount
            isLoading={isLoading}
            start={data.start_index}
            end={data.end_index}
            totalResults={data.results_total_count}
          />
          <p className="govuk-body govuk-!-margin-bottom-0">
            <a
              href=""
              onClick={handleClearFilters}
              className="govuk-link govuk-link--no-visited-state
                    "
            >
              Clear all filters
            </a>
          </p>
        </div>
        {docTypeQuery.length > 0 || publisherQuery.length > 0 ? (
          <AppliedFilters
            documentTypeCheckedState={documentTypeCheckedState}
            publisherCheckedState={publisherCheckedState}
            removeFilter={handleDeleteFilter}
            publishers={publishers}
          />
        ) : (
          <hr className="govuk-section-break govuk-section-break--m govuk-section-break--visible" />
        )}
        <SortSelect sortQuery={sortQuery[0]} setSortQuery={setSortQuery} />
        <hr className="govuk-section-break govuk-section-break--m govuk-section-break--visible" />
        {data.results_total_count === 0 && !isLoading ? (
          <NoResultsContent />
        ) : (
          <Results results={data.results} isLoading={isLoading} searchQuery={searchQuery[0]} />
        )}

        <Pagination pageData={data} pageQuery={pageQuery[0]} setPageQuery={setPageQuery} />
      </div>
    </div>
  )
}

export default App
