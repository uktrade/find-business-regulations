import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { DevToggle } from "../DevToggle"

describe("DevToggle", () => {
  const mockSetAppsToDisplay = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    document.body.innerHTML = '<div id="fbr-django-search"></div>'
  })

  test("renders checkboxes", () => {
    const appsToDisplay = { reactApp: true, djangoApp: true }

    render(<DevToggle appsToDisplay={appsToDisplay} setAppsToDisplay={mockSetAppsToDisplay} />)

    expect(screen.getByLabelText("React app")).toBeInTheDocument()
    expect(screen.getByLabelText("Django app")).toBeInTheDocument()
  })

  test("toggles React app checkbox", () => {
    const appsToDisplay = { reactApp: true, djangoApp: true }

    render(<DevToggle appsToDisplay={appsToDisplay} setAppsToDisplay={mockSetAppsToDisplay} />)

    fireEvent.click(screen.getByLabelText("React app"))
    expect(mockSetAppsToDisplay).toHaveBeenCalledWith({ reactApp: false, djangoApp: true })
  })

  test("toggles Django app checkbox", () => {
    const appsToDisplay = { reactApp: true, djangoApp: true }

    render(<DevToggle appsToDisplay={appsToDisplay} setAppsToDisplay={mockSetAppsToDisplay} />)

    fireEvent.click(screen.getByLabelText("Django app"))
    expect(mockSetAppsToDisplay).toHaveBeenCalledWith({ reactApp: true, djangoApp: false })
    expect(document.getElementById("fbr-django-search").style.display).toBe("none")
  })

  test("updates Django app display on mount", () => {
    const appsToDisplay = { reactApp: true, djangoApp: false }

    render(<DevToggle appsToDisplay={appsToDisplay} setAppsToDisplay={mockSetAppsToDisplay} />)

    expect(document.getElementById("fbr-django-search").style.display).toBe("none")
  })
})
