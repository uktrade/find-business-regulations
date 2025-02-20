function Pagination({ pageData, pageQuery, setPageQuery }) {
  const handlePreviousPage = (e) => {
    e.preventDefault()
    setPageQuery([parseInt(pageQuery) - 1])
  }

  const handleNextPage = (e) => {
    e.preventDefault()
    setPageQuery([parseInt(pageQuery) + 1])
  }

  const { current_page, is_paginated, results_page_total } = pageData

  // Generate page range array from results_page_total
  const page_range = Array.from({ length: results_page_total }, (_, i) => i + 1)

  const isPreviousPage = current_page - 1 >= 1
  const isNextPage = current_page + 1 <= results_page_total

  return is_paginated ? (
    <nav className="govuk-pagination" role="navigation" aria-label="Pagination">
      {isPreviousPage ? (
        <div className="govuk-pagination__prev">
          <a
            className="govuk-link govuk-pagination__link govuk-link--no-visited-state"
            href="#"
            onClick={handlePreviousPage}
            role="button"
            aria-label="Previous page"
          >
            <svg
              className="govuk-pagination__icon govuk-pagination__icon--prev"
              xmlns="http://www.w3.org/2000/svg"
              height="13"
              width="15"
              aria-hidden="true"
              focusable="false"
              viewBox="0 0 15 13"
            >
              <path d="m6.5938-0.0078125-6.7266 6.7266 6.7441 6.4062 1.377-1.449-4.1856-3.9768h12.896v-2h-12.984l4.2931-4.293-1.414-1.414z"></path>
            </svg>
            <span className="govuk-pagination__link-title">
              Previous<span className="govuk-visually-hidden"> page</span>
            </span>
          </a>
        </div>
      ) : null}
      <ul className="govuk-pagination__list">
        {page_range.map((page_number) => {
          if (page_number === current_page) {
            return (
              <li key={page_number} className="govuk-pagination__item govuk-pagination__item--current">
                <a
                  className="govuk-link govuk-pagination__link govuk-link--no-visited-state"
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    setPageQuery([page_number])
                  }}
                  role="button"
                  aria-current={current_page === page_number ? "page" : undefined}
                >
                  {page_number}
                </a>
              </li>
            )
          } else if (
            page_number === 1 ||
            page_number === results_page_total ||
            page_number === current_page - 1 ||
            page_number === current_page + 1
          ) {
            return (
              <li key={page_number} className="govuk-pagination__item">
                <a
                  className="govuk-link govuk-pagination__link"
                  href="#"
                  onClick={(e) => {
                    e.preventDefault()
                    setPageQuery([page_number])
                  }}
                  role="button"
                  aria-label={`Page ${page_number}`}
                >
                  {page_number}
                </a>
              </li>
            )
          } else if (page_number === current_page - 2 || page_number === current_page + 2) {
            return (
              <li key={page_number} className="govuk-pagination__item govuk-pagination__item--ellipses">
                &hellip;
              </li>
            )
          }
        })}
      </ul>
      {isNextPage ? (
        <div className="govuk-pagination__next">
          <a
            className="govuk-link govuk-pagination__link govuk-link--no-visited-state"
            href="#"
            onClick={handleNextPage}
            aria-label="Next page"
          >
            <span className="govuk-pagination__link-title">
              Next<span className="govuk-visually-hidden"> page</span>
            </span>
            <svg
              className="govuk-pagination__icon govuk-pagination__icon--next"
              xmlns="http://www.w3.org/2000/svg"
              height="13"
              width="15"
              aria-hidden="true"
              focusable="false"
              viewBox="0 0 15 13"
            >
              <path d="m8.4062 13.007 6.7266-6.7266-6.7441-6.4062-1.377 1.449 4.1856 3.9768h-12.896v2h12.984l-4.2931 4.293 1.414 1.414z"></path>
            </svg>
          </a>
        </div>
      ) : null}
    </nav>
  ) : null
}

export { Pagination }
