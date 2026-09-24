(function () {
    "use strict";

    const script = document.currentScript;

    if (!script) {
        console.error("FlyRank Widget: Could not find the script element.");
        return;
    }

    const widgetId = script.getAttribute("data-widget-id");

    if (!widgetId) {
        console.error(
            "FlyRank Widget: Missing data-widget-id attribute."
        );
        return;
    }

    const API_BASE_URL = "http://127.0.0.1:8000";

    async function loadWidget() {
        try {
            const response = await fetch(
                `${API_BASE_URL}/widgets/public/${widgetId}`
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to load widget: HTTP ${response.status}`
                );
            }

            const widget = await response.json();

            renderWidget(widget);
        } catch (error) {
            console.error(
                "FlyRank Widget: Failed to load widget.",
                error
            );
        }
    }

    function renderWidget(widget) {
        const container = document.createElement("div");

        container.className = "flyrank-widget";

        container.style.maxWidth = "400px";
        container.style.padding = "20px";
        container.style.border = "1px solid #ddd";
        container.style.borderRadius = "10px";
        container.style.backgroundColor = "#ffffff";
        container.style.fontFamily = "Arial, sans-serif";
        container.style.boxSizing = "border-box";

        const title = document.createElement("h2");

        title.textContent = widget.title;

        title.style.marginTop = "0";
        title.style.marginBottom = "10px";

        container.appendChild(title);

        if (widget.description) {
            const description = document.createElement("p");

            description.textContent = widget.description;

            description.style.marginBottom = "15px";

            container.appendChild(description);
        }

        const form = document.createElement("form");

        form.style.marginTop = "15px";

        const fields = widget.fields || {};

        Object.entries(fields).forEach(([fieldName, fieldType]) => {
            const wrapper = document.createElement("div");

            wrapper.style.marginBottom = "12px";

            const label = document.createElement("label");

            label.textContent = fieldName;
            label.htmlFor = `flyrank-${fieldName}`;

            label.style.display = "block";
            label.style.marginBottom = "5px";
            label.style.fontWeight = "bold";

            const input = document.createElement("input");

            input.id = `flyrank-${fieldName}`;
            input.name = fieldName;
            input.type = fieldType || "text";
            input.required = true;

            input.style.width = "100%";
            input.style.padding = "10px";
            input.style.border = "1px solid #ccc";
            input.style.borderRadius = "6px";
            input.style.boxSizing = "border-box";

            wrapper.appendChild(label);
            wrapper.appendChild(input);

            form.appendChild(wrapper);
        });

        // Honeypot field.
        // Humans should never see or fill this field.
        const honeypot = document.createElement("input");

        honeypot.type = "text";
        honeypot.name = "website";
        honeypot.autocomplete = "off";
        honeypot.tabIndex = -1;

        honeypot.style.position = "absolute";
        honeypot.style.left = "-9999px";
        honeypot.style.width = "1px";
        honeypot.style.height = "1px";
        honeypot.style.opacity = "0";

        form.appendChild(honeypot);

        const button = document.createElement("button");

        button.type = "submit";
        button.textContent = widget.button_text || "Submit";

        button.style.padding = "10px 16px";
        button.style.border = "none";
        button.style.borderRadius = "6px";
        button.style.cursor = "pointer";

        form.appendChild(button);

        const message = document.createElement("p");

        message.style.marginTop = "15px";

        form.appendChild(message);

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            button.disabled = true;
            message.textContent = "Submitting...";

            const formData = new FormData(form);

            const data = {};

            for (const [key, value] of formData.entries()) {
                if (key !== "website") {
                    data[key] = value;
                }
            }

            const idempotencyKey =
                `${widgetId}-${Date.now()}-${Math.random()
                    .toString(36)
                    .substring(2, 10)}`;

            try {
                const response = await fetch(
                    `${API_BASE_URL}/public/submissions`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            widget_id: widgetId,
                            data: data,
                            honeypot: formData.get("website") || "",
                            idempotency_key: idempotencyKey
                        })
                    }
                );

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(
                        result.detail || "Submission failed."
                    );
                }

                if (result.status === "success") {
                    message.textContent =
                        "Thank you! Your submission was received.";

                    form.reset();
                } else {
                    message.textContent =
                        result.message || "Submission received.";
                }

            } catch (error) {
                console.error(
                    "FlyRank Widget: Submission failed.",
                    error
                );

                message.textContent =
                    error.message || "Something went wrong.";

            } finally {
                button.disabled = false;
            }
        });

        container.appendChild(form);

        script.parentNode.insertBefore(
            container,
            script.nextSibling
        );
    }

    loadWidget();
})();