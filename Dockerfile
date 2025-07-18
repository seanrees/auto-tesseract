FROM python:3

# Install necessary binaries:
#   tesseract (with English, Irish and French language packs for OCR)
#   ImageMagick (for PDF conversion)
#   ghostscript for PDF
RUN apt update
RUN apt install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-gle tesseract-ocr-fra imagemagick ghostscript

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

# Fix an issue with ImageMagick that results in this error:
# attempt to perform an operation not allowed by the security policy `PDF'
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

USER nobody

VOLUME /app/in
VOLUME /app/out

ENTRYPOINT ["/app/auto_tesseract.py", "--in_dir", "/app/in", "--out_dir", "/app/out"]
