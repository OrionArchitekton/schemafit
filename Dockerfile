FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .

# Run as non-root.
RUN useradd --create-home --uid 10001 schemafit
USER schemafit

WORKDIR /work
ENTRYPOINT ["python", "-m", "schemafit"]
CMD ["demo"]
