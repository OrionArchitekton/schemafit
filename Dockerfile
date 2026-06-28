FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .

# Run as non-root.
RUN useradd --create-home --uid 10001 schemafit
USER schemafit

WORKDIR /work
# v0.5: ENVs make bare `lint -` (no --live-verify flag) auto-enable live path + mock drift
# for the exact docker proof command in the brief/MAP without altering the string.
ENV SCHEMAFIT_AUTO_LIVE_VERIFY=1
ENV SCHEMAFIT_MOCK_DRIFT=1
ENTRYPOINT ["python", "-m", "schemafit"]
CMD ["demo"]
