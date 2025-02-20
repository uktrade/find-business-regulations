const DRF_API_URL = "/api/v1"
export const SEARCH_URL = `${DRF_API_URL}/search/`
export const PUBLISHERS_URL = `${DRF_API_URL}/retrieve/publishers/`

// These should come from the API/Django backend, but for now they are hardcoded
export const DOCUMENT_TYPES = [
  {
    name: "legislation",
    label: "Legislation",
  },
  {
    name: "guidance",
    label: "Guidance",
  },
  {
    name: "standard",
    label: "Standards",
  },
]
