package engineclient

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestRunEngineStreamsAndParsesNDJSON(t *testing.T) {
	fakePython := writeFakePython(t, `#!/usr/bin/env sh
cat >/dev/null
printf '%s\n' '{"protocol_version":"rygnal.engine.v1","request_id":"req-1","timestamp":"2026-06-15T00:00:00.000Z","event":"engine.started","ok":true,"status":"starting","data":{},"error":null}'
printf '%s\n' '{"protocol_version":"rygnal.engine.v1","request_id":"req-1","timestamp":"2026-06-15T00:00:00.000Z","event":"run.completed","ok":true,"status":"completed","data":{"status":"completed"},"error":null}'
`)

	var rawLines []string
	var events []EngineEvent

	result, err := RunEngine(
		context.Background(),
		EngineOptions{
			RequestID:       "req-1",
			TrustedRepoPath: "/tmp/trusted-repo",
			AgentArgs:       []string{"python", "agent.py"},
			UnsafeLocal:     true,
			DebugMode:       false,
			TimeoutSec:      30,
			PythonPath:      fakePython,
			WorkDir:         filepath.Dir(fakePython),
		},
		func(rawLine string, event EngineEvent) error {
			rawLines = append(rawLines, rawLine)
			events = append(events, event)
			return nil
		},
	)

	if err != nil {
		t.Fatalf("RunEngine returned error: %v", err)
	}

	if result.EventCount != 2 {
		t.Fatalf("expected two events, got %d", result.EventCount)
	}

	if len(rawLines) != 2 || len(events) != 2 {
		t.Fatalf("expected two streamed events, got raw=%d parsed=%d", len(rawLines), len(events))
	}

	if events[1].Event != "run.completed" {
		t.Fatalf("unexpected final event: %+v", events[1])
	}
}

func TestRunEngineRejectsInvalidNDJSON(t *testing.T) {
	fakePython := writeFakePython(t, `#!/usr/bin/env sh
cat >/dev/null
printf '%s\n' 'not-json'
`)

	_, err := RunEngine(
		context.Background(),
		EngineOptions{
			RequestID:       "req-1",
			TrustedRepoPath: "/tmp/trusted-repo",
			AgentArgs:       []string{"python", "agent.py"},
			UnsafeLocal:     true,
			TimeoutSec:      30,
			PythonPath:      fakePython,
			WorkDir:         filepath.Dir(fakePython),
		},
		nil,
	)

	if err == nil {
		t.Fatal("expected invalid NDJSON to fail")
	}

	if !strings.Contains(err.Error(), "engine protocol error") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestRunEngineHonorsContextTimeout(t *testing.T) {
	fakePython := writeFakePython(t, `#!/usr/bin/env sh
sleep 5
`)

	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	_, err := RunEngine(
		ctx,
		EngineOptions{
			RequestID:       "req-1",
			TrustedRepoPath: "/tmp/trusted-repo",
			AgentArgs:       []string{"python", "agent.py"},
			UnsafeLocal:     true,
			TimeoutSec:      30,
			PythonPath:      fakePython,
			WorkDir:         filepath.Dir(fakePython),
		},
		nil,
	)

	if err == nil {
		t.Fatal("expected timeout to fail")
	}

	if !strings.Contains(err.Error(), "timed out") &&
		!strings.Contains(err.Error(), "cancelled") &&
		!strings.Contains(err.Error(), "killed") {
		t.Fatalf("unexpected timeout error: %v", err)
	}
}

func writeFakePython(t *testing.T, script string) string {
	t.Helper()

	path := filepath.Join(t.TempDir(), "fake-python")
	if err := os.WriteFile(path, []byte(script), 0o755); err != nil {
		t.Fatalf("write fake python: %v", err)
	}

	return path
}
