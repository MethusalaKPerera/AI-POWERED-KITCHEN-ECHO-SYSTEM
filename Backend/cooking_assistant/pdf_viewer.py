#!/usr/bin/env python3
"""
PDF Content Viewer
Simple tool to see what text is actually in your PDFs
"""

from pathlib import Path

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("❌ pdfplumber not installed!")
    print("Install: pip install pdfplumber PyPDF2 --break-system-packages")

def view_pdf_content(pdf_path, max_pages=5):
    """View first few pages of PDF"""
    
    if not PDF_AVAILABLE:
        return
    
    print("\n" + "="*70)
    print(f"VIEWING PDF: {pdf_path}")
    print("="*70 + "\n")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            print(f"Showing first {min(max_pages, total_pages)} pages...\n")
            
            for i in range(min(max_pages, total_pages)):
                page = pdf.pages[i]
                text = page.extract_text()
                
                print(f"{'='*70}")
                print(f"PAGE {i+1}")
                print(f"{'='*70}")
                
                if text:
                    # Show first 1000 characters
                    print(text[:1000])
                    if len(text) > 1000:
                        print(f"\n... (page has {len(text)} total characters)")
                else:
                    print("⚠️ No text found (might be scanned image)")
                
                print()
    
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("PDF CONTENT VIEWER")
    print("="*70)
    
    if not PDF_AVAILABLE:
        return
    
    # Find PDFs
    pdf_folder = Path('pdf_cookbooks')
    if not pdf_folder.exists():
        print(f"\n❌ Folder not found: {pdf_folder}")
        return
    
    pdfs = list(pdf_folder.glob('*.pdf'))
    
    if not pdfs:
        print(f"\n❌ No PDFs in {pdf_folder}/")
        return
    
    print(f"\nFound {len(pdfs)} PDFs:\n")
    for i, pdf in enumerate(pdfs, 1):
        print(f"  {i}. {pdf.name}")
    
    choice = input(f"\nSelect PDF to view (1-{len(pdfs)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pdfs):
            view_pdf_content(str(pdfs[idx]))
        else:
            print("Invalid selection")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    main()