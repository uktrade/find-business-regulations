import { useState, useEffect, useMemo, useCallback, useRef } from "react"
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

/**
 * Generates an array of boolean values based on which checkboxes match the query values
 *
 * @param {Array} checkboxes - Array of checkbox objects with name properties
 * @param {Array} queryValues - Array of selected values from the URL query
 * @returns {Array} - Array of boolean values indicating checked state
 */
const generateCheckedState = (checkboxes, queryValues) => {
  return checkboxes.map(({ name }) => queryValues.includes(name))
}

/**
 * Main application component that handles search functionality, filters, and results display
 */
function App() {
  // URL query parameters with their default values
  const [searchQuery, setSearchQuery] = useQueryParams("search", [])
  const [docTypeQuery, setDocTypeQuery] = useQueryParams("document_type", [])
  const [publisherQuery, setPublisherQuery] = useQueryParams("publisher", [])
  const [sortQuery, setSortQuery] = useQueryParams("sort", ["recent"])
  const [pageQuery, setPageQuery] = useQueryParams("page", [1])

  // Local state
  const [searchInput, setSearchInput] = useState(searchQuery[0] || "") // Current search input text
  const [data, setData] = useState([]) // API response data
  const [isLoading, setIsLoading] = useState(true) // Loading state for API calls
  const [isSearchSubmitted, setIsSearchSubmitted] = useState(false) // Flag to track search form submission
  const [publishers, setPublishers] = useState([]) // List of publishers fetched from API
  const [publisherCheckedState, setPublisherCheckedState] = useState([]) // Checked state for publisher filters
  const [pageTitle, setPageTitle] = useState("Find business regulations") // Browser tab title

  // Track whether this is the first search after page load
  // Used to automatically switch sort to "relevance" on first search
  const isFirstRender = useRef(true)

  // Fetch the list of publishers on component mount
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

  // Initialize document type filter checked states
  // Memoized to avoid recalculation on every render
  const initialDocumentTypeCheckedState = useMemo(
    () => generateCheckedState(DOCUMENT_TYPES, docTypeQuery),
    [docTypeQuery],
  )
  const [documentTypeCheckedState, setDocumentTypeCheckedState] = useState(initialDocumentTypeCheckedState)

  // Handle changes to the search input
  // Memoized to avoid recreation on every render
  const handleSearchChange = useCallback(
    (event) => {
      setSearchInput(event.target.value)
    },
    [setSearchInput],
  )

  /**
   * Handle removing a filter from the applied filters
   *
   * @param {string} filterName - Type of filter ("docType" or "publisher")
   * @param {string} filter - Value of the filter to remove
   */
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

  /**
   * Handle clearing all applied filters
   *
   * @param {Event} event - Click event
   */
  const handleClearFilters = (event) => {
    event.preventDefault()
    setDocTypeQuery([])
    setPublisherQuery([])
    setDocumentTypeCheckedState(generateCheckedState(DOCUMENT_TYPES, []))
    setPublisherCheckedState(generateCheckedState(publishers, []))
  }

  /**
   * Fetch data with loading state management
   *
   * @param {Object} queryString - Object with query parameters
   */
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

  /**
   * Handle search form submission
   * Updates URL query params and fetches results
   */
  const handleSearchSubmit = useCallback(() => {
    setIsSearchSubmitted(true)
    setSearchQuery([searchInput])
    setPageQuery([1]) // Reset to first page on new search

    // Check if this is the first call with search input
    const isFirstCallWithSearchInput = searchInput.length > 0 && isFirstRender.current

    // Determine the sort value to use for the API call
    const sortValue = isFirstCallWithSearchInput ? "relevance" : sortQuery[0]

    // Switch sort to "relevance" if a search term is entered and this is the first search
    // This ensures that the first search prioritizes relevance while preserving user sort choice afterwards
    if (isFirstCallWithSearchInput) {
      setSortQuery(["relevance"])
    }

    // Mark that the first render has occurred
    isFirstRender.current = false

    // Build filter parameters for the API request
    const filterParams = {
      ...(searchInput.length > 0 && { search: searchInput }),
      ...(docTypeQuery.length > 0 && { document_type: docTypeQuery }),
      ...(publisherQuery.length > 0 && { publisher: publisherQuery }),
      sort: sortValue,
      page: [1],
    }

    fetchDataWithLoading(filterParams)
  }, [searchInput, docTypeQuery, publisherQuery, sortQuery, setPageQuery])

  /**
   * Handle clicking on a publisher in the search results
   * Adds the publisher to the filter if not already included
   *
   * @param {string} publisherKey - The publisher identifier to add
   * @returns {boolean} - False if publisher already in filters
   */
  const handlePublisherClick = (publisherKey) => {
    // Prevent adding duplicate publishers to the filter
    if (publisherQuery.includes(publisherKey)) return false

    const updatedPublisherQuery = [...publisherQuery, publisherKey]
    setPublisherQuery(updatedPublisherQuery)
    setPublisherCheckedState(generateCheckedState(publishers, updatedPublisherQuery))
  }

  // Fetch data when URL parameters change (e.g., from back/forward navigation)
  // Uses debounce to avoid excessive API calls
  useEffect(() => {
    // Skip if the change was from a form submission (handleSearchSubmit already fetches data)
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
    }, 300) // Debounce delay

    // Clean up timeout on component unmount or dependency change
    return () => {
      clearTimeout(handler)
    }
  }, [searchQuery, docTypeQuery, publisherQuery, sortQuery, pageQuery])

  // Update page title based on search query and page number
  useEffect(() => {
    if (searchQuery.length > 0) {
      const newTitle = `${searchQuery.join(", ")} - page ${pageQuery[0]} - Find business regulations`
      setPageTitle(newTitle)
    } else {
      setPageTitle("Find business regulations")
    }
  }, [searchQuery, pageQuery])

  // Update the document title when pageTitle changes
  useEffect(() => {
    document.title = pageTitle
  }, [pageTitle])

  return (
    <div className="govuk-grid-row search-form">
      {/* Left sidebar with search and filters */}
      <div className="govuk-grid-column-one-third">
        <Search
          handleSearchChange={handleSearchChange}
          searchInput={searchInput}
          handleSearchSubmit={handleSearchSubmit}
        />
        {/* Document type filter */}
        <div className="govuk-form-group ">
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--m">
              <h2 className="govuk-fieldset__heading">Document type</h2>
            </legend>
            <CheckboxFilter
              checkboxGroupName="document_type"
              checkboxData={DOCUMENT_TYPES}
              checkedState={documentTypeCheckedState}
              setCheckedState={setDocumentTypeCheckedState}
              setQueryParams={setDocTypeQuery}
              withSearch={false}
              setIsLoading={setIsLoading}
            />
          </fieldset>
        </div>
        {/* Publisher filter */}
        <div className="govuk-form-group">
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--m">
              <h2 className="govuk-fieldset__heading">Published by</h2>
            </legend>
            {publishers ? (
              <CheckboxFilter
                checkboxGroupName="publishers"
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
        {/* CSV download link */}
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

      {/* Main content area with search results */}
      <div className="govuk-grid-column-two-thirds">
        {/* Results count and clear filters section */}
        <div className="fbr-flex fbr-flex--space-between">
          <ResultsCount
            isLoading={isLoading}
            start={data.start_index}
            end={data.end_index}
            totalResults={data.results_total_count}
            searchQuery={searchQuery[0]}
          />
          <p className="govuk-body govuk-!-margin-bottom-0">
            <a href="" onClick={handleClearFilters} className="govuk-link govuk-link--no-visited-state">
              Clear all filters
            </a>
          </p>
        </div>

        {/* Display applied filters if any */}
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

        {/* Sort selector */}
        <SortSelect sortQuery={sortQuery[0]} setSortQuery={setSortQuery} />
        <hr className="govuk-section-break govuk-section-break--m govuk-section-break--visible" />

        {/* Search results heading (visually hidden for accessibility) */}
        <h2 className="govuk-heading-l govuk-visually-hidden">Search results</h2>

        {/* Display results or no results message */}
        {data.results_total_count === 0 && !isLoading ? (
          <NoResultsContent />
        ) : (
          <Results
            results={data.results}
            isLoading={isLoading}
            searchQuery={searchQuery[0]}
            publishers={publishers}
            onPublisherClick={handlePublisherClick}
          />
        )}

        {/* Pagination controls */}
        <Pagination pageData={data} pageQuery={pageQuery[0]} setPageQuery={setPageQuery} />
      </div>
    </div>
  )
}

export default App
