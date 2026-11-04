[View the MCO review architecture diagram](output/mco-review.html) · [Source JSON](output/candidate.json)

CLI and MCP reviews converge on a shared runtime that runs selected providers concurrently and returns their individual answers in declaration order, retaining failures alongside successes.

The diagram includes source references and process/filesystem boundaries. It covers the default shim path; external provider internals remain explicitly unknown. Automated checks passed, and laptop-size rendering was visually reviewed. Application and Archify source remain unchanged.