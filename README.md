# Documentation claim auditor

This offline static auditor compares documentation of the checked capability with Python source patterns. It scans the root README and Markdown under docs. Fenced code is excluded; inline code counts. Source is parsed without execution. Tests are reported separately; fixtures, examples, documentation and symlinks are excluded from production evidence.

```sh
pdf-splitting-claim-audit audit . --json --fail-on medium --ignore vendor/
python3 -m pdf_splitting_claim_audit --version
```

Exit 0 means PASS, 2 means a finding meets the threshold, and 1 means a usage or I/O error. The default threshold is high. Ignore prefixes can be repeated.

```
documented-pdf-splitting-claim-false
documented-no-pdf-splitting-claim-false
```

## Differentiation

The checked operation is distinct from document extraction, generation and merging, spreadsheet, word processing and presentation reading or generation, table extraction, invoice and other document extraction, invoice separation, multiple receipt detection, document cropping, electronic signatures, payment processing and OCR. Those claim categories are outside this tool's phrase lists.

## Limitations

Exact phrases can describe form fields, annotations, version control, page images or text, in-memory page objects, bookmark or chapter lists, or a preview widget rather than the checked capability. Static patterns are not semantic judgment: dead code counts, some alias chains are missed, and denial handling depends on the listed phrases.

Pairs and triples are matched within a module, not on the same variable. Unrelated calls can satisfy a route. A reader and writer with a page-adding call count even if only one page is added; the number of output files is not tracked. A selection of one page counts. A slice that covers the whole document also counts; the tool does not check that it is a proper subset.

A reader alone, a writer with a page-adding call but no reader, or a reader and writer without a page-adding call does not count. Bare page-adding or selection calls require the corresponding constructions or opener. Extending whole pages without a subscript, appending a single page, plural page addition, writer append or merge, and insertion into another document are not detected. An opener followed only by save is copying and does not count. Combining files and generating documents from content are outside the evidence routes. External commands including pdfseparate, qpdf and Ghostscript are not detected.

Mindee, Azure, Veryfi, Google Document AI, Eden AI, Textract, LlamaParse, Nanonets, Docsumo, ABBYY Vantage, Rossum, Klippa, Parseur and Extend calls are not detected: these services use extraction operations or opaque identifiers. Hand-written object-stream parsing is not detected. Encrypted inputs require decryption; the tool cannot determine whether an input is encrypted.
