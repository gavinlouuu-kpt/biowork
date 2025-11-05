# ddPCR sample always visible in Import page

Change: The Import page now always shows the ddPCR sample dataset regardless of `FF_SAMPLE_DATASETS`.

- File updated: `web/apps/labelstudio/src/pages/CreateProject/Import/Import.jsx`
- Logic: when `FF_SAMPLE_DATASETS` is off, we pass a ddPCR-only list to `SampleDatasetSelect`; when on, we pass all samples.
- ddPCR sample source: `web/apps/labelstudio/src/pages/CreateProject/Import/samples.json`
- No backend changes required.

Verification
- With feature flags disabled, the sample dropdown still contains "ddPCR Images"; with flags enabled, all samples appear.
