---
name: convert-books-to-markdown
description: Convert EPUB, PDF, DOCX, or TXT books, collections, transcripts, handouts, and question lists into clean, structured Obsidian-compatible Markdown. Use when the user asks to extract, split, organize, rename, clean, or repair book/document conversions; preserve source hierarchy and illustrations; remove page numbers, copyright/promotional matter, or duplicate files; create native Obsidian footnotes and links; or verify a previously converted Markdown library.
---

# Convert Books to Markdown

Convert the supplied document into a faithful, clean Markdown library that opens correctly in Obsidian. Treat the user's newest book-specific instruction as an override; otherwise apply every default below.

## Establish the source structure

1. Inspect the source before writing output.
2. Derive reading order from semantic structure, not archive filename order:
   - For EPUB, parse `container.xml`, OPF spine, NAV/NCX, XHTML anchors, and image resources. Detect a duplicate table of contents embedded at the end.
   - For PDF, inspect rendered sample pages and use layout-aware extraction. Use OCR only for scanned pages, and verify uncertain text visually.
   - For DOCX, use heading styles plus visible season, episode, chapter, and section markers.
   - For TXT, infer hierarchy from its outline, numbering, and repeated separators.
3. Build a source-to-output outline before conversion. Do not treat every TOC entry as a separate file: distinguish books, parts, chapters, sections, captions, notes, and index entries.
4. Preserve the source's language and meaningful wording. Never invent missing text or silently repair uncertain OCR.
5. Before conversion, determine whether the source contains meaningful machine-readable body text. If it consists only of full-page scans, page images, or an image collection with no substantive extractable text, skip it: do not OCR it, generate Markdown, copy its images, or create a ZIP unless the user explicitly requests conversion of that specific image-only source. Record the content hash as skipped so automated checks do not repeatedly treat it as new.

## Use the output location

- Default to `/Users/echo/Downloads/输出`.
- For books, name the root folder `<short book title> by <author>`.
- For magazines, journals, newspapers, newsletters, and other periodicals, group every issue under one publication folder. Name each issue `<publication title> YYYY-MM-DD`, for example `The Economist 2026-01-03`, so issues sort chronologically within that publication folder. Use a month-only date as `YYYY-MM` only when the source identifies no reliable day. Do not append `by <publisher>` or `by <publication>`.
- Do not create a ZIP archive unless the user explicitly requests one. When requested, use the root-folder name unchanged as the ZIP basename and do not append `Markdown - Clean` or another conversion-status suffix.
- Derive the author from reliable source metadata or visible book content, preserving the source language and meaningful author wording. If the author cannot be identified reliably, ask the user before final naming instead of guessing.
- Put images in `_assets` under the root folder.
- Do not write to the source directory or an iCloud/Obsidian directory unless explicitly requested.
- Build in a staging directory, validate it, then synchronize it to the destination. Inspect an existing destination before replacing it; preserve user edits and ask before an uncertain overwrite.

## Split and organize files

- Create one Markdown file per semantic reading unit—normally one chapter, article, story, section, episode, or user-specified secondary heading. Do not combine the entire work into one file unless explicitly requested.
- Keep subsections within their chapter as Markdown headings instead of over-splitting.
- If the source contains Parts, create one numbered folder per Part and place its chapters directly inside.
- Number Part folders consecutively from `01` in source reading order. Do not use the cumulative chapter position as a Part-folder prefix.
- Within each Part folder, restart sortable content-file prefixes at `01` and continue without gaps. Preserve meaningful source chapter numbering in the visible title or H1.
- If the source hierarchy does not unambiguously determine whether numbering should restart, ask the user before naming folders or files.
- If a work exceeds 40 chapters and is divided into Parts, require one folder per Part.
- For a collected works edition, use `genre / work / chapter.md`; delete publisher catalogues and promotional excerpts.
- For a television transcript, use `season / episode.md`.
- When a folder would contain only one content file, use the actual title and omit a redundant `Chapter 01` prefix.
- Avoid redundant single-child nesting. For example, put individual diaries directly in `09 日记` rather than adding another `01 日记` folder.
- Put front matter and back matter directly in the book root by default. Do not create `00` or `99` folders unless explicitly requested.

## Name folders and files

- Prefix sortable content with zero-padded Arabic sequence numbers: `01`, `02`, ….
- Do not repeat a number already represented by the sortable prefix. For example, use `01 Title.md`, not `01 1 Title.md`, and never create both `Chapter 1` and `Chapter 01` copies.
- Preserve source Roman chapter numerals when they are meaningful, while prepending the sortable Arabic sequence: `08 Chapter VIII - Title.md`.
- Preserve the source's `Chapter` wording unless the user requests its removal. Do not add `Chapter` to folder names by default.
- Use `00` for retained front matter and `99` for retained back matter. If several files exist, use `00 - 01`, `00 - 02` and `99 - 01`, `99 - 02`; if only one exists, omit the trailing `- 01`.
- Keep Epilogue as a distinct ordered unit or folder when the source treats it as one.
- Sanitize filesystem-illegal characters without changing visible meaning.
- Treat renaming rules stated for a particular book as local overrides, not permanent global rules.

## Clean and format content

- Start every file with one H1 title. Skip the same title from the extracted body so it does not appear twice.
- Convert the source hierarchy to H2/H3 headings while preserving paragraph, list, table, blockquote, emphasis, and line-break semantics.
- Reflow prose for normal screen reading: remove line endings, word breaks, and column transitions caused only by the printed layout. Keep blank lines between semantic paragraphs; do not reproduce the source's narrow columns or page-width wrapping in Markdown.
- Remove printed page numbers, running headers, running footers, blank pagination artifacts, and page-anchor IDs from body text.
- Remove covers, title pages, copyright pages, piracy disclaimers, download-site advertising, publisher promotion, and unrelated catalogues by default.
- Retain substantive authorial front matter and back matter unless the user requests deletion.
- Remove stray bracket markers such as `[]` or `[12]` only when they are conversion artifacts or when the user explicitly requests it. Never destroy valid Markdown links or native footnotes.
- Do not duplicate title text merely because it appears in the filename, source heading, and first paragraph.
- Preserve the original reading order. Exclude duplicate HTML tables of contents or repeated EPUB spine resources.

## Preserve images at suitable sizes

- Retain meaningful illustrations, diagrams, tables rendered as images, and their captions. Remove cover art, publisher logos, and decorative promotion unless requested.
- Preserve original aspect ratio and never upscale a small image.
- Because the library is read primarily in Obsidian, use Obsidian embeds for local images by default: `![[_assets/example.jpg]]`. Keep paths relative to the vault and preserve spaces normally; do not percent-encode wikilink paths. Use Markdown image syntax only when a requested external renderer requires it, and use HTML only when exact display dimensions materially matter.
- Set a practical display width according to the original proportions: approximately 420–560 px for portraits, 650–800 px for ordinary landscapes, and 850–1000 px for very wide scrolls or tables. Add `max-width: 100%; height: auto` when using HTML.
- Keep paired images and captions together. Verify every referenced asset exists.
- If the user asks to remove images from one named book, remove both image markup and unused asset files only from that output.

## Convert notes, indexes, and links

- Convert source notes to native Obsidian footnotes: references as `[^id]` and definitions as `[^id]: text`.
- Keep footnote identifiers unique within each Markdown file and verify that every reference has one definition and vice versa.
- Convert reliable internal cross-references to Obsidian wikilinks by default, using aliases when the visible label differs: `[[file name|visible title]]`. Use Markdown anchor links only when a requested external renderer requires them.
- Preserve a substantive index. Remove original page numbers; when source mapping is reliable and the user requests inline annotations, attach index information to the relevant body text with native footnotes or direct internal links.
- If page-only index mapping cannot be reconstructed reliably, retain a cleaned standalone index without page numbers and report the limitation instead of guessing.

## Validate before delivery

1. Run `scripts/validate_markdown_output.py <output-folder>` on the staged output.
2. Correct every reported error. Review warnings manually.
3. Compare the staged and destination trees after synchronization.
4. Run the validator again on the destination with `--settle-seconds 2` to catch delayed Finder/cloud duplicate copies.
5. If the user explicitly requested a ZIP, test the archive and compare its checksum after copying.
6. Confirm all of the following before claiming completion:
   - the source was not an image-only document that should have been skipped;
   - expected Markdown and asset counts;
   - no names such as `Title 2.md`, `Title (2).md`, or duplicate `Chapter 1`/`Chapter 01` variants;
   - Part folders are consecutively numbered with no gaps, and each Part's direct content files begin at `01` and progress consecutively with no gaps;
   - no exact or whitespace-normalized duplicate Markdown content;
   - no broken local image or file links;
   - matched native footnote references and definitions;
   - no repeated opening title;
   - no residual copyright, piracy, download-site, publisher-promotion, or duplicate-TOC text;
   - no source page numbers in body text.

## Report the result

- Lead with a clickable absolute link to the destination folder. Include a ZIP link only when the user explicitly requested an archive.
- State the Markdown and image counts.
- Summarize material cleanup, structural choices, and footnote/index treatment.
- Explicitly state the post-sync duplicate-check result. Do not say the files are updated or synchronized until the destination itself has been rechecked.
