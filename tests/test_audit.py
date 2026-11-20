EXPECTED_YES = ('split pdf', 'splits pdf', 'splitting pdf', 'split pdfs', 'splits pdfs', 'splitting pdfs', 'split pdf file', 'splits pdf file', 'splitting pdf file', 'split pdf files', 'splits pdf files', 'splitting pdf files', 'split pdf document', 'splits pdf document', 'splitting pdf document', 'split pdf documents', 'split pdf into pages', 'splits pdf into pages', 'splitting pdf into pages', 'split pdf into separate files', 'split pdf into separate pdfs', 'split pdf by page', 'splits pdf by page', 'splitting pdf by page', 'split pdf pages', 'splits pdf pages', 'splitting pdf pages', 'extract pages from pdf', 'extracts pages from pdf', 'extracting pages from pdf', 'split multiple pdfs', 'splits multiple pdfs', 'splitting multiple pdfs', 'pdf splitter', 'pdf splitting', 'pdf split', 'split a pdf', 'splits a pdf', 'splitting a pdf', 'split one pdf', 'split pdf into parts', 'splits pdf into parts', 'splitting pdf into parts', 'split pdf into chapters', 'split pdf into single pages', 'split pdf into individual pages', 'split pdf by chapter', 'split pdf by bookmark', 'pdf page splitter', 'pdf page splitting')
EXPECTED_NO = ('no pdf splitting', 'does not split pdf', 'does not split pdfs', 'does not split pdf files', 'does not split pdf document', 'does not split pdf documents', 'does not split pdf into pages', 'does not split pdf by page', 'does not extract pages from pdf', 'no pdf splitter', 'no pdf split', 'does not support pdf splitting', 'without pdf splitting', 'pdf splitting not supported', 'no pdf splitting support', 'does not split multiple pdfs', 'does not split pdf into separate files', 'does not split pdf into parts', 'does not split pdf into single pages', 'does not split pdf into individual pages', 'does not split pdf pages', 'does not split a pdf', 'does not split one pdf', 'does not split pdf into chapters')
EXPECTED_NAMES = ('split_pdf', 'split_pdfs', 'split_pdf_file', 'split_pdf_files', 'split_pdf_document', 'split_pdf_documents', 'split_pdf_pages', 'split_pdf_by_page', 'split_pdf_into_pages', 'split_pdf_into_files', 'split_pdf_into_parts', 'split_pdf_into_chapters', 'extract_pdf_pages', 'extract_pages_from_pdf', 'pdf_splitter', 'pdf_split', 'pdf_page_splitter', 'split_pdf_by_chapter', 'split_pdf_by_bookmark', 'split_pdf_by_range', 'split_pdf_range', 'split_pdf_at_page', 'pdf_split_into_pages', 'split_pdf_pages_out')
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from pdf_splitting_claim_audit.audit import audit, evidence
from pdf_splitting_claim_audit.phrases import PDFSPLITTING, NOPDFSPLITTING, GENERIC_NAMES
from pdf_splitting_claim_audit.__main__ import main

class AuditTests(unittest.TestCase):
    def test_phrase_oracle(self):
        self.assertEqual(PDFSPLITTING, EXPECTED_YES)
        self.assertEqual(NOPDFSPLITTING, EXPECTED_NO)
        self.assertEqual(GENERIC_NAMES, EXPECTED_NAMES)

    def test_routes(self):
        cases = [
            'from pypdf import PdfReader, PdfWriter\nPdfReader(x); PdfWriter(); w.add_page(x)',
            'import pypdf\npypdf.PdfReader(x); pypdf.PdfWriter(); w.add_page(x)',
            'import pypdf as p\np.PdfReader(x); p.PdfWriter(); w.add_page(x)',
            'from PyPDF2 import PdfReader, PdfWriter\nPdfReader(x); PdfWriter(); w.add_page(x)',
            'import PyPDF2\nPyPDF2.PdfReader(x); PyPDF2.PdfWriter(); w.add_page(x)',
            'from PyPDF2 import PdfReader, PdfFileWriter\nPdfReader(x); PdfFileWriter(); w.add_page(x)',
            'from fitz import open as op\nop(x); d.select(x)', 'import fitz\nfitz.open(x); d.select(x)',
            'import fitz\nfitz.open(); d.select(x)', 'from fitz import Document\nDocument(x); d.select(x)',
            'import fitz\nfitz.Document(x); d.select(x)', 'import pymupdf\npymupdf.open(x); d.select(x)',
            'import pymupdf\npymupdf.Document(x); d.select(x)',
            'import pikepdf\npikepdf.Pdf.open(x); d.pages.extend(src.pages[0:3])',
            'from pikepdf import open as op\nop(x); d.pages.extend(src.pages[i:j])',
            'import pikepdf\npikepdf.Pdf.new(); d.pages.extend(src.pages[0:3])',
            'from pikepdf import new\nnew(); d.pages.extend(src.pages[0:3])',
            'from pikepdf import Pdf as P\nP.open(x); d.pages.extend(src.pages[0:3])',
            'from pdfrw import PdfReader, PdfWriter\nPdfReader(x); PdfWriter(); w.addpage(x)',
            'import pdfrw\npdfrw.PdfReader(x); pdfrw.PdfWriter(); w.addpage(x)',
            'from pdfrw import PdfReader, PdfFileWriter\nPdfReader(x); PdfFileWriter(); w.addpage(x)',
            'from other import split_pdf as sp\nsp(x)']
        cases += ['x.' + name + '(x)' for name in EXPECTED_NAMES]
        for source in cases:
            with self.subTest(source=source): self.assertTrue(evidence(source))

    def test_not_evidence(self):
        cases = ['import '+x for x in ('pypdf','PyPDF2','fitz','pymupdf','pikepdf','pdfrw')]
        cases += ['import pypdf\npypdf.PdfReader(x)', 'import pypdf\npypdf.PdfWriter()',
                  'import pypdf\npypdf.PdfWriter().add_page(x)', 'import pypdf\npypdf.PdfReader(x); pypdf.PdfWriter()',
                  'x.add_page(y)', 'import PyPDF2\nPyPDF2.PdfWriter().append(x)', 'import PyPDF2\nPyPDF2.PdfWriter().merge(x)',
                  'import fitz\nfitz.open(x)', 'import fitz\nfitz.open()', 'x.select(y)', 'import fitz\nfitz.open(x).save(x)',
                  'import fitz\nfitz.open(x).insert_pdf(x)', 'import pikepdf\npikepdf.Pdf.open(x)', 'import pikepdf\npikepdf.new()',
                  'x.pages.extend(y[0:3])', 'import pikepdf\npikepdf.open(x); d.pages.extend(src.pages)',
                  'import pikepdf\npikepdf.new(); d.pages.append(x)', 'import pikepdf\npikepdf.open(); d.pages.extend(src.pages[0:3])',
                  'import pdfrw\npdfrw.PdfReader(x)', 'import pdfrw\npdfrw.PdfWriter()',
                  'import pdfrw\npdfrw.PdfWriter().addpage(x)', 'x.addpage(y)', 'x.addpages(y)',
                  'import pdfplumber\npdfplumber.open(x)', 'from pdfminer.high_level import extract_text\nextract_text(x)',
                  'import reportlab\nreportlab.Canvas(x).save()', 'import fitz\nfitz.open().insert_text(x); x.save()',
                  '"pdf"', 'x.split_pdf', 'def split_pdf(): pass\nx.split_pdf()',
                  'import pypdf\npypdf=1\npypdf.PdfReader(x); pypdf.PdfWriter(); w.add_page(x)',
                  'from pypdf import PdfReader, PdfWriter\nwith x as PdfReader: pass\nPdfReader(x); PdfWriter(); w.add_page(x)', 'def broken(']
        cases += ['import subprocess\nsubprocess.run(["'+x+'", "x"])' for x in ('pdfseparate','qpdf','gs')]
        cases += [x+'(x)' for x in ('mindee.parse','azure.begin_analyze_document','veryfi.Client','documentai.process_document','textract.analyze_document','eden.universal_ai','llamaparse.parse','nanonets.ocr','docsumo.upload','abbyy.process','rossum.process','klippa.parse','parseur.parse','extend.parse')]
        for source in cases:
            with self.subTest(source=source): self.assertFalse(evidence(source))

    def test_audit_scenarios(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); readme=p/'README.md'; src=p/'app.py'
            readme.write_text('split pdf files'); r=audit(d); self.assertEqual(r['findings'][0]['severity'],'HIGH'); self.assertEqual(r['verdict'],'FAIL')
            src.write_text('import fitz\nfitz.open(); d.select(x)'); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('does not split pdf files'); r=audit(d); self.assertEqual(r['findings'][0]['rule'],'documented-no-pdf-splitting-claim-false'); self.assertEqual(r['claims'],[])
            src.unlink(); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('```\nsplit pdf files\n```'); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('`split pdf files`'); self.assertEqual(audit(d)['verdict'],'FAIL')
            (p/'tests').mkdir(); (p/'tests/test_app.py').write_text('import fitz\nfitz.open(); d.select(x)')
            self.assertEqual(audit(d)['findings'][0]['severity'],'MEDIUM'); self.assertEqual(audit(d)['verdict'],'PASS'); self.assertEqual(audit(d, fail_on='medium')['verdict'],'FAIL')
            src.write_text('import fitz\nfitz.open()'); (p/'other.py').write_text('x.select(y)'); self.assertEqual(audit(d)['findings'][0]['severity'],'MEDIUM')
            readme.write_text('Nothing claimed'); self.assertEqual(audit(d)['verdict'],'PASS')

    def test_exclusions(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'README.md').write_text('split pdf')
            for name in ('fixtures','examples','docs'):
                (p/name).mkdir(); (p/name/'code.py').write_text('x.split_pdf()')
            (p/'test_file.py').write_text('x.split_pdf()'); (p/'app_test.py').write_text('x.split_pdf()')
            (p/'link.py').symlink_to(p/'test_file.py'); (p/'linked').symlink_to(p/'fixtures', target_is_directory=True)
            r=audit(d); self.assertFalse(r['production_evidence']); self.assertEqual(len(r['test_evidence']),2)
            self.assertEqual(audit(d, ignore=('test_', 'app_'))['findings'][0]['severity'],'HIGH')

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'README.md').write_text('split pdf')
            cmd=[sys.executable, '-m', 'pdf_splitting_claim_audit']
            r=subprocess.run(cmd+['audit',d,'--json'],capture_output=True,text=True); self.assertEqual(r.returncode,2)
            data=json.loads(r.stdout); self.assertEqual(data['verdict'],'FAIL'); self.assertEqual(data['findings'][0]['rule'],'documented-pdf-splitting-claim-false'); self.assertTrue(data['findings'][0]['message'])
            self.assertEqual(subprocess.run(cmd+['--version'],capture_output=True,text=True).stdout.strip(),'0.1.0')
            self.assertEqual(subprocess.run(cmd+['audit',d,'--fail-on','HIGH'],capture_output=True).returncode,1)
            self.assertEqual(subprocess.run(cmd+['audit',d+'/missing'],capture_output=True).returncode,1)
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(['audit',d]),2)
            (p/'README.md').write_text('does not split pdf'); (p/'app.py').write_text('x.split_pdf()')
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(['audit',d]),2)
            (p/'app.py').unlink(); (p/'README.md').write_text('split pdf'); (p/'test_app.py').write_text('x.split_pdf()')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['audit',d]),0); self.assertEqual(main(['audit',d,'--fail-on','medium']),2)
