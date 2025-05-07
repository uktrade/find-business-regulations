from django import forms


class CookiePreferenceForm(forms.Form):
    """Cookie page preference form.

    Radio Select Form for setting Google Analytics (GA) consent cookies. This
    form is rendered in the cookies page.

    Note: We want to set the value of the GA cookie to "true" or "false" rather
    than a boolean values so that the GTM script can read the value correctly.
    """

    cookie_preference = forms.ChoiceField(
        label="Do you want to accept analytics cookies?",
        choices=(("true", "Yes"), ("false", "No")),
        widget=forms.RadioSelect,
        required=False,
    )


class RegulationSearchForm(forms.Form):
    """Regulation Search Form.

    Regulation search form for searching
    for regulations by name or description.
    """

    search = forms.CharField(
        required=False,
        label="Search",
        help_text="",
        widget=forms.TextInput(
            attrs={
                "class": "govuk-input search-input",
                "id": "search",
                "name": "search",
                "type": "search",
                "placeholder": "",
            }
        ),
    )

    document_type = forms.MultipleChoiceField(
        required=False,
        choices=[
            ("legislation", "Legislation"),
            ("guidance", "Guidance"),
            ("standard", "Standards"),
        ],
        # widget=forms.CheckboxSelectMultiple(
        #     attrs={
        #         "class": "govuk-checkboxes__input",
        #         "data-module": "govuk-checkboxes",
        #     }
        # ),
        # label="Select document types",
        # help_text="You can select multiple document types.",
    )

    publisher = forms.MultipleChoiceField(
        required=False,
        choices=[
            ("healthandsafetyexecutive", "Health and Safety Executive"),
            ("civilaviationauthority", "Civil Aviation Authority"),
            ("environmentagency", "Environment Agency"),
            ("defra", "Defra"),
            (
                "officeofgasandelectricitymarkets",
                "Office of Gas and Electricity Markets",
            ),
            ("officeofrailandroad", "Office of Rail and Road"),
            ("naturalengland", "Natural England"),
            ("historicengland", "Historic England"),
            ("nationalhighways", "National Highways"),
            ("homesengland", "Homes England"),
            ("departmentfortransport", "Department for Transport"),
        ],
    )

    sort = forms.ChoiceField(
        # initial="relevance",
        required=False,
        label="Sort by",
        choices=[
            ("recent", "Recently updated"),
            ("relevance", "Relevance"),
        ],
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
                "id": "sort",
                "name": "sort",
                "onChange": "form.submit()",
            }
        ),
    )


class EmailForm(forms.Form):
    """Email form for sending test emails via GOV.UK Notify."""

    feedback = forms.CharField(
        label="Tell us how we can improve",
        max_length=10000,
        help_text="Include information and links that will help us understand, investigate and correct any problems you've found.",  # noqa: E501
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 4,
                "id": "feedback",
            }
        ),
        error_messages={
            "required": "Enter your feedback or report a problem",
            "max_length": "Feedback must be 1,200 characters or less",
        },
    )

    email = forms.EmailField(
        label="Your email address",
        help_text="We'll only use this if we need to find out more about your comments.",  # noqa: E501
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "govuk-input",
                "id": "email",
            }
        ),
        error_messages={
            "required": "Enter an email address in the correct format, like name@example.com",  # noqa: E501
            "invalid": "Enter an email address in the correct format, like name@example.com",  # noqa: E501
        },
    )
