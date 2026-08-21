document.addEventListener("DOMContentLoaded", () => {
    const version =
        typeof DOCUMENTATION_OPTIONS === "undefined"
            ? null
            : DOCUMENTATION_OPTIONS.VERSION;
    if (!version) return;

    for (const brand of document.querySelectorAll(".sidebar-brand")) {
        const label = document.createElement("small");
        label.className = "sidebar-brand-version";
        label.textContent = `version ${version}`;
        brand.append(label);
    }
});
