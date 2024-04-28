function updateExporters(exporters) {
    for (const exporter of exporters) {
        exporter.isDefault = false;
    }
    exporters.push({
        extension: "csv",
        label: "My fancy CSV",
        showDeckList: true,
        showIncludeScheduling: false,
        showIncludeDeckConfigs: false,
        showIncludeMedia: false,
        showIncludeTags: false,
        showIncludeHtml: false,
        showLegacySupport: false,
        showIncludeDeck: false,
        showIncludeNotetype: false,
        showIncludeGuid: false,
        isDefault: true,
        doExport: (outPath, limit, options) => {
            alert("Not implemented!");
            return Promise.resolve();
        }
    });
    return exporters;
}

addEventListener("exportersDidInitialize", (event) => event.detail.exporters.update(updateExporters));
