//go:build windows

package engineclient

import "os/exec"

func configureManagedProcess(_ *exec.Cmd) {}

func terminateProcessTree(cmd *exec.Cmd) error {
	if cmd.Process == nil {
		return nil
	}

	return cmd.Process.Kill()
}
