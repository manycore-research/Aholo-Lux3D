# Task metadata and local timing

Tasks are keyed by explicit region plus the exact decimal-string task ID.
Local snapshot timestamps never establish provider creation time or duration.
A supplied taskMetadata record may provide creation time only under this shape:

```json
{
  "schema": "lux3d.task-metadata/v1",
  "taskId": "123",
  "region": "cn",
  "created": 1735689600123,
  "observedAt": "2025-01-01T00:01:00Z",
  "source": {
    "method": "GET",
    "path": "/lux3d/v1/generate/task/list",
    "field": "items[].created",
    "unit": "unix-milliseconds",
    "page": 1,
    "pageSize": 100
  }
}
```

Replace example facts with real captured values; omit the record when absent.
The delivery module validates the binding but performs no service lookup.
Provider duration and settled-charge placeholders remain unavailable for
manifest compatibility. Pages omit credits; quoting and submission authorization
are unchanged.

## Local end-to-end time

The runner fixes `localCompletedAt` on first local success; for 3D artifacts,
after download, validation and the single-task manifest write. Each attempt
exposes `localStartedAt` (workflow `createdAt`), `localCompletedAt` and their
wall-clock difference `localDurationMs`, including submission, polling and
resume waits. Preserve completion across metadata refreshes and page rebuilds.

Report attempts separately, without summing parallel durations. Missing
completion stays unavailable, including legacy successful states; never infer
it from `updatedAt`, provider `lastModified` or preview rebuild time. Invalid
intervals are rejected; zero is valid. This is not server execution time.
