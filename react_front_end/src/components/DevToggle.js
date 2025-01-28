import { useEffect } from "react"

function DevToggle({ appsToDisplay, setAppsToDisplay }) {
  const djangoAppDiv = document.getElementById("fbr-django-search")

  useEffect(() => {
    if (djangoAppDiv) {
      djangoAppDiv.style.display = appsToDisplay.djangoApp ? "block" : "none"
    }
  })

  const toggleReactApp = () => {
    setAppsToDisplay({
      ...appsToDisplay,
      reactApp: !appsToDisplay.reactApp,
    })
  }

  const toggleDjangoApp = () => {
    djangoAppDiv.style.display = appsToDisplay.djangoApp ? "none" : "block"
    setAppsToDisplay({
      ...appsToDisplay,
      djangoApp: !appsToDisplay.djangoApp,
    })
  }

  return (
    <div
      style={{
        position: "fixed",
        top: "-5px",
        right: "-5px",
        padding: "10px 10px 5px 5px",
        backgroundColor: "white",
        border: "1px solid black",
        borderRadius: "5px",
        zIndex: "1000",
        fontFamily: "Arial, sans-serif",
        fontSize: "14px",
        textAlign: "right",
      }}
    >
      <label htmlFor="react">React app</label>
      <input type="checkbox" id="react" name="react" checked={appsToDisplay.reactApp} onChange={toggleReactApp} />
      <br />
      <label htmlFor="django">Django app</label>
      <input type="checkbox" id="django" name="django" checked={appsToDisplay.djangoApp} onChange={toggleDjangoApp} />
    </div>
  )
}

export { DevToggle }
