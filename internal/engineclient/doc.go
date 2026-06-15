// Package engineclient owns the Go-to-Python NDJSON stdio bridge.
//
// It starts python -m rygnal.engine_api as a managed child process, writes one
// strict JSON request to stdin, and validates every stdout line as Rygnal
// EngineEvent NDJSON before exposing it to the CLI renderer.
package engineclient
