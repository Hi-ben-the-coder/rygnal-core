package cli

import (
	"bytes"
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/Rygnal/rygnal-core/internal/engineclient"
)

func TestVersionCommand(t *testing.T) {
	stdout, stderr, err := executeForTest("version")

	if err != nil {
		t.Fatalf("version returned error: %v", err)
	}

	if stderr != "" {
		t.Fatalf("expected empty stderr, got %q", stderr)
	}

	if !strings.Contains(stdout, "rygnal version 0.1.0") {
		t.Fatalf("unexpected stdout: %q", stdout)
	}
}

func TestRunRequiresDoubleDashSeparator(t *testing.T) {
	_, _, err := executeForTest("run", "python", "agent.py")

	if err == nil {
		t.Fatal("expected missing -- separator to fail")
	}

	if !strings.Contains(err.Error(), "double-dash '--' separator is required") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestRunRejectsEmptyAgentCommand(t *testing.T) {
	_, _, err := executeForTest("run", "--")

	if err == nil {
		t.Fatal("expected empty agent command to fail")
	}

	if !strings.Contains(err.Error(), "agent command cannot be empty") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestRunRejectsInvalidTimeout(t *testing.T) {
	_, _, err := executeForTest("run", "--timeout", "0", "--", "python", "agent.py")

	if err == nil {
		t.Fatal("expected invalid timeout to fail")
	}

	if !strings.Contains(err.Error(), "--timeout must be greater than zero") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestRunJSONPassesRawEngineNDJSON(t *testing.T) {
	deps := fakeRunDependencies(t)

	stdout, stderr, err := executeForTestWithDeps(
		deps,
		"run",
		"--json",
		"--unsafe-local",
		"--timeout",
		"45",
		"--",
		"python",
		"agent.py",
	)

	if err != nil {
		t.Fatalf("run returned error: %v", err)
	}

	if stderr != "" {
		t.Fatalf("expected empty stderr in json mode, got %q", stderr)
	}

	if !strings.Contains(stdout, `"event":"engine.started"`) {
		t.Fatalf("expected raw engine NDJSON, got %q", stdout)
	}

	if !strings.Contains(stdout, `"event":"run.completed"`) {
		t.Fatalf("expected final raw event, got %q", stdout)
	}
}

func TestRunHumanRendersEngineLifecycle(t *testing.T) {
	deps := fakeRunDependencies(t)

	stdout, stderr, err := executeForTestWithDeps(
		deps,
		"run",
		"--unsafe-local",
		"--timeout",
		"45",
		"--",
		"python",
		"agent.py",
		"--verbose",
	)

	if err != nil {
		t.Fatalf("run returned error: %v", err)
	}

	if !strings.Contains(stderr, "WARNING: Running with --unsafe-local") {
		t.Fatalf("expected unsafe-local warning, got stderr %q", stderr)
	}

	expectedFragments := []string{
		"Rygnal engine started",
		"Request accepted by Python engine",
		"Run completed: status=completed",
	}

	for _, fragment := range expectedFragments {
		if !strings.Contains(stdout, fragment) {
			t.Fatalf("stdout missing %q:\n%s", fragment, stdout)
		}
	}
}

func TestRunPropagatesEngineError(t *testing.T) {
	deps := fakeRunDependencies(t)
	deps.runEngine = func(
		context.Context,
		engineclient.EngineOptions,
		engineclient.EventHandler,
	) (engineclient.Result, error) {
		return engineclient.Result{}, errors.New("engine bridge failed")
	}

	_, _, err := executeForTestWithDeps(deps, "run", "--", "python", "agent.py")

	if err == nil {
		t.Fatal("expected engine error")
	}

	if !strings.Contains(err.Error(), "engine bridge failed") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func fakeRunDependencies(t *testing.T) runDependencies {
	t.Helper()

	return runDependencies{
		resolveGitRoot: func() (string, error) {
			return "/tmp/trusted-repo", nil
		},
		resolveEngineRoot: func() (string, error) {
			return "/tmp/rygnal-engine-root", nil
		},
		newRequestID: func() (string, error) {
			return "test-request-id", nil
		},
		runEngine: func(
			_ context.Context,
			opts engineclient.EngineOptions,
			handler engineclient.EventHandler,
		) (engineclient.Result, error) {
			if opts.TrustedRepoPath != "/tmp/trusted-repo" {
				t.Fatalf("unexpected trusted repo path: %q", opts.TrustedRepoPath)
			}

			if opts.WorkDir != "/tmp/rygnal-engine-root" {
				t.Fatalf("unexpected engine workdir: %q", opts.WorkDir)
			}

			if opts.RequestID != "test-request-id" {
				t.Fatalf("unexpected request id: %q", opts.RequestID)
			}

			if strings.Join(opts.AgentArgs, " ") != "python agent.py --verbose" &&
				strings.Join(opts.AgentArgs, " ") != "python agent.py" {
				t.Fatalf("unexpected agent args: %v", opts.AgentArgs)
			}

			started := engineclient.EngineEvent{
				ProtocolVersion: engineclient.ProtocolVersion,
				RequestID:       "test-request-id",
				Event:           "engine.started",
				OK:              true,
				Status:          "starting",
				Data:            []byte(`{}`),
			}
			accepted := engineclient.EngineEvent{
				ProtocolVersion: engineclient.ProtocolVersion,
				RequestID:       "test-request-id",
				Event:           "request.accepted",
				OK:              true,
				Status:          "accepted",
				Data:            []byte(`{"action":"guarded_run.start"}`),
			}
			completed := engineclient.EngineEvent{
				ProtocolVersion: engineclient.ProtocolVersion,
				RequestID:       "test-request-id",
				Event:           "run.completed",
				OK:              true,
				Status:          "completed",
				Data:            []byte(`{"status":"completed"}`),
			}

			if err := handler(
				`{"protocol_version":"rygnal.engine.v1","request_id":"test-request-id","timestamp":"2026-06-15T00:00:00.000Z","event":"engine.started","ok":true,"status":"starting","data":{},"error":null}`,
				started,
			); err != nil {
				return engineclient.Result{}, err
			}

			if err := handler(
				`{"protocol_version":"rygnal.engine.v1","request_id":"test-request-id","timestamp":"2026-06-15T00:00:00.000Z","event":"request.accepted","ok":true,"status":"accepted","data":{"action":"guarded_run.start"},"error":null}`,
				accepted,
			); err != nil {
				return engineclient.Result{}, err
			}

			if err := handler(
				`{"protocol_version":"rygnal.engine.v1","request_id":"test-request-id","timestamp":"2026-06-15T00:00:00.000Z","event":"run.completed","ok":true,"status":"completed","data":{"status":"completed"},"error":null}`,
				completed,
			); err != nil {
				return engineclient.Result{}, err
			}

			return engineclient.Result{
				EventCount: 3,
				LastEvent:  &completed,
			}, nil
		},
	}
}

func executeForTest(args ...string) (string, string, error) {
	return executeForTestWithDeps(defaultRunDependencies(), args...)
}

func executeForTestWithDeps(deps runDependencies, args ...string) (string, string, error) {
	cmd := NewRootCommand()
	cmd.SetArgs(args)

	for _, command := range cmd.Commands() {
		if command.Name() == "run" {
			cmd.RemoveCommand(command)
			break
		}
	}
	cmd.AddCommand(newRunCmdWithDependencies(deps))

	var stdout bytes.Buffer
	var stderr bytes.Buffer

	cmd.SetOut(&stdout)
	cmd.SetErr(&stderr)

	err := cmd.Execute()

	return stdout.String(), stderr.String(), err
}
